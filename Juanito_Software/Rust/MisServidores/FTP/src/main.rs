//! Servidor FTP mínimo: solo std, sin crates externos.
//! Soporta USER, PASS, SYST, PWD, CWD, TYPE I, PASV, LIST, RETR, STOR,
//! NOOP y QUIT.
//!
//! ADVERTENCIA DE SEGURIDAD
//! ========================
//! Este servidor NO implementa TLS/FTPS/SFTP: las credenciales (USER/PASS) y
//! todo el contenido transferido viajan en claro por la red. La comparación
//! de credenciales es de tiempo constante y solo evita fallos de
//! temporización; NO cifra nada. Use este servidor únicamente en entornos
//! locales o redes de confianza.
//!
//! Configuración por variables de entorno (ver README para el detalle):
//!
//!   FTP_HOST                  IPv4 literal de escucha. Por defecto 127.0.0.1.
//!   FTP_PORT                  Puerto TCP. Por defecto 2121. 0 = efímero (tests).
//!   FTP_ROOT                  Raíz FTP. Por defecto el directorio "storage"
//!                             junto al binario (NO el directorio de trabajo
//!                             del proceso). Se crea si no existe y se
//!                             resuelve UNA sola vez al arrancar.
//!   FTP_USUARIO / FTP_CLAVE   Credenciales. OBLIGATORIAS; sin ellas no arranca.
//!   FTP_MAX_CLIENTS           Sesiones concurrentes máximas. Por defecto 10.
//!   FTP_MAX_UPLOAD_BYTES      Tamaño máximo de subida (STOR). 50 MiB por defecto.
//!   FTP_MAX_COMMAND_BYTES     Máximo de bytes por línea de control. 8192.
//!   FTP_CONTROL_TIMEOUT       Segundos de inactividad del canal de control.
//!   FTP_DATA_CONNECT_TIMEOUT  Segundos para establecer el canal de datos PASV.
//!   FTP_DATA_TIMEOUT          Segundos de inactividad durante una transferencia.
//!   FTP_MAX_LOGIN_ATTEMPTS    Intentos fallidos de PASS por sesión. 3.
//!   FTP_PASV_ADDRESS          Dirección IPv4 que se anuncia en PASV. Si falta
//!                             se usa FTP_HOST, salvo que esta sea 0.0.0.0 (en
//!                             ese caso el arranque falla: no se anuncia
//!                             0.0.0.0 automáticamente).
//!
//! GARANTÍAS DE SISTEMA DE ARCHIVOS (y sus límites)
//! ================================================
//! - Las rutas FTP se resuelven contra la raíz virtual "/" con la función
//!   común `resolver_ruta`: componentes "." / ".." confinados en la raíz,
//!   componentes con prefijo de unidad ("C:") rechazados, y contención
//!   verificada por componentes sobre la raíz canónica (`starts_with` compara
//!   componentes completos, no cadenas).
//! - Política de enlaces simbólicos: se SIGUEN (canonicalizar los resuelve),
//!   pero el destino final debe quedar contenido en la raíz canónica; un
//!   enlace que apunte fuera de la raíz se rechaza. Esto NO es una
//!   protección absoluta frente a carreras TOCTOU: entre la validación y la
//!   apertura, un atacante con permisos de escritura en la raíz podría
//!   sustituir componentes por enlaces simbólicos. Operaciones basadas en
//!   descriptores de directorio (openat/O_NOFOLLOW) ofrecerían mayor
//!   garantía pero no están disponibles de forma portable en std; aquí no se
//!   usan y la limitación queda documentada. `canonicalize()` seguido de
//!   `open()` NO resuelve por sí solo estos ataques.
//! - STOR usa un archivo temporal creado con `create_new` (O_EXCL) en el
//!   directorio de destino y la publica con `fs::rename` (atómico en el mismo
//!   volumen, NTFS/POSIX). Las subidas incompletas NUNCA reemplazan el
//!   archivo previo. STOR sí sobrescribe archivos existentes (como hacía
//!   `File::create`), pero solo tras recibir y sincronizar el archivo
//!   completo. Un destino que ya sea enlace simbólico se rechaza.
//! - Diferencias POSIX/Windows: `fs::rename` reemplaza el destino en ambos
//!   (en Windows usa MOVEFILE_REPLACE_EXISTING); O_NOFOLLOW no existe en
//!   Windows y los enlaces simbólicos requieren privilegios; la protección
//!   frente a enlaces en destino de escritura es best-effort en Windows.
//! - Durabilidad: se hace `flush()` + `sync_all()` antes de publicar y un
//!   error de `sync_all` cancela la publicación (no se ignora). El directorio
//!   no se sincroniza (fsync de directorio no es portable en Windows), por lo
//!   que tras un corte de energía el nombre podría perderse aunque el
//!   contenido esté en disco.

use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, Read, Write};
use std::net::{IpAddr, Ipv4Addr, Shutdown, TcpListener, TcpStream};
use std::path::{Component, Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

/// Límite de entradas en un LIST.
const MAX_ENTRADAS_LIST: usize = 10_000;
/// Límite de bytes enviados en un LIST.
const MAX_BYTES_LIST: usize = 4 * 1024 * 1024;
/// Tamaño de bloque de transferencia de datos.
const BLOQUE_DATOS: usize = 64 * 1024;
/// Intervalo de sondeo del accept() acotado del canal de datos.
const INTERVALO_ACEPTAR: Duration = Duration::from_millis(25);

// ---------------------------------------------------------------------------
// Configuración: lectura del entorno y validación al arrancar
// ---------------------------------------------------------------------------

/// Configuración completa del servidor, ya validada.
struct Config {
    host: Ipv4Addr,
    port: u16,
    root: PathBuf,
    usuario: String,
    clave: String,
    max_clients: usize,
    max_upload_bytes: u64,
    max_command_bytes: usize,
    control_timeout: Duration,
    data_connect_timeout: Duration,
    data_timeout: Duration,
    max_login_attempts: u32,
    pasv_address: Ipv4Addr,
}

fn entorno_cadena(vars: &HashMap<String, String>, nombre: &str) -> Option<String> {
    vars.get(nombre).filter(|v| !v.is_empty()).cloned()
}

fn entorno_entero(
    vars: &HashMap<String, String>,
    nombre: &str,
    predeterminado: u64,
    minimo: u64,
    maximo: u64,
) -> Result<u64, String> {
    let Some(valor) = vars.get(nombre).filter(|v| !v.is_empty()) else {
        return Ok(predeterminado);
    };
    let v: u64 = valor
        .parse()
        .map_err(|_| format!("Valor inválido para {nombre}: '{valor}' debe ser un entero"))?;
    if v < minimo {
        return Err(format!(
            "Valor inválido para {nombre}: {v} debe ser >= {minimo}"
        ));
    }
    if v > maximo {
        return Err(format!(
            "Valor inválido para {nombre}: {v} debe ser <= {maximo}"
        ));
    }
    Ok(v)
}

fn entorno_ipv4(vars: &HashMap<String, String>, nombre: &str) -> Result<Ipv4Addr, String> {
    let Some(valor) = entorno_cadena(vars, nombre) else {
        return Err(format!("Falta la variable {nombre}"));
    };
    valor.parse::<Ipv4Addr>().map_err(|_| {
        format!("Valor inválido para {nombre}: '{valor}' debe ser una dirección IPv4 literal")
    })
}

/// Raíz predeterminada: el directorio "storage" JUNTO AL BINARIO, no el
/// directorio de trabajo del proceso (que depende de dónde se lance y no es
/// un lugar estable para datos). Se documenta en el README.
fn raiz_predeterminada() -> Result<PathBuf, String> {
    let exe = std::env::current_exe()
        .map_err(|e| format!("No se pudo determinar la ruta del binario: {e}"))?;
    let dir = exe
        .parent()
        .ok_or_else(|| "No se pudo determinar el directorio del binario".to_string())?;
    Ok(dir.join("storage"))
}

/// Crea la raíz si no existe, la canóniza y comprueba que es un directorio
/// utilizable para escritura (sonda con creación exclusiva que se borra).
fn preparar_raiz(ruta: &Path) -> Result<PathBuf, String> {
    fs::create_dir_all(ruta)
        .map_err(|e| format!("No se pudo crear la raíz FTP {}: {e}", ruta.display()))?;
    let canon = fs::canonicalize(ruta)
        .map_err(|e| format!("No se pudo resolver la raíz FTP {}: {e}", ruta.display()))?;
    let meta = fs::metadata(&canon)
        .map_err(|e| format!("La raíz FTP {} no es accesible: {e}", canon.display()))?;
    if !meta.is_dir() {
        return Err(format!(
            "La raíz FTP {} no es un directorio",
            canon.display()
        ));
    }
    static CONTADOR_SONDA: AtomicU64 = AtomicU64::new(0);
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    let sonda = canon.join(format!(
        ".ftp-sonda-{}-{nanos}-{}",
        std::process::id(),
        CONTADOR_SONDA.fetch_add(1, Ordering::Relaxed)
    ));
    match File::options().write(true).create_new(true).open(&sonda) {
        Ok(mut f) => {
            let escritura = f.write_all(b"sonda").and_then(|_| f.sync_all());
            drop(f);
            let _ = fs::remove_file(&sonda);
            escritura.map_err(|e| {
                format!(
                    "La raíz FTP {} no admite escritura: {e}",
                    canon.display()
                )
            })?;
        }
        Err(e) => {
            return Err(format!(
                "La raíz FTP {} no admite creación de archivos: {e}",
                canon.display()
            ))
        }
    }
    Ok(canon)
}

/// Valida toda la configuración al arrancar. Cualquier error es fatal y se
/// comunica con un mensaje claro (el caller termina el proceso).
fn validar_configuracion(vars: &HashMap<String, String>) -> Result<Config, String> {
    let host = entorno_ipv4(vars, "FTP_HOST").or_else(|e| {
        if entorno_cadena(vars, "FTP_HOST").is_none() {
            Ok(Ipv4Addr::new(127, 0, 0, 1))
        } else {
            Err(e)
        }
    })?;
    let port = entorno_entero(vars, "FTP_PORT", 2121, 0, 65535)? as u16;

    let root = match entorno_cadena(vars, "FTP_ROOT") {
        Some(ruta) => PathBuf::from(ruta),
        None => raiz_predeterminada()?,
    };
    let root = preparar_raiz(&root)?;

    let usuario = entorno_cadena(vars, "FTP_USUARIO").ok_or_else(|| {
        "No se puede arrancar sin credenciales.\n\
         Define las variables de entorno FTP_USUARIO y FTP_CLAVE antes de ejecutar:\n\
         \x20 Windows : set FTP_USUARIO=juan  &&  set FTP_CLAVE=tu_clave\n\
         \x20 Linux   : export FTP_USUARIO=juan FTP_CLAVE=tu_clave"
            .to_string()
    })?;
    let clave = entorno_cadena(vars, "FTP_CLAVE").ok_or_else(|| {
        "No se puede arrancar sin credenciales: falta FTP_CLAVE (FTP_USUARIO está definido)."
            .to_string()
    })?;

    let max_clients = entorno_entero(vars, "FTP_MAX_CLIENTS", 10, 1, 1000)? as usize;
    let max_upload_bytes = entorno_entero(vars, "FTP_MAX_UPLOAD_BYTES", 50 * 1024 * 1024, 1, u64::MAX)?;
    let max_command_bytes = entorno_entero(vars, "FTP_MAX_COMMAND_BYTES", 8192, 64, 65536)? as usize;
    let control_timeout =
        Duration::from_secs(entorno_entero(vars, "FTP_CONTROL_TIMEOUT", 300, 1, 3600)?);
    let data_connect_timeout =
        Duration::from_secs(entorno_entero(vars, "FTP_DATA_CONNECT_TIMEOUT", 10, 1, 300)?);
    let data_timeout = Duration::from_secs(entorno_entero(vars, "FTP_DATA_TIMEOUT", 300, 1, 3600)?);
    let max_login_attempts = entorno_entero(vars, "FTP_MAX_LOGIN_ATTEMPTS", 3, 1, 20)? as u32;

    let pasv_address = match entorno_cadena(vars, "FTP_PASV_ADDRESS") {
        Some(valor) => valor.parse::<Ipv4Addr>().map_err(|_| {
            format!(
                "Valor inválido para FTP_PASV_ADDRESS: '{valor}' debe ser una dirección IPv4 literal"
            )
        })?,
        None => host,
    };
    if pasv_address.is_unspecified() {
        return Err(
            "FTP_PASV_ADDRESS no puede ser 0.0.0.0: hay que anunciar una dirección \
             alcanzable por el cliente (127.0.0.1 en local, la IP de LAN, o la IP \
             pública si hay NAT con reenvío de puertos)."
                .to_string(),
        );
    }

    Ok(Config {
        host,
        port,
        root,
        usuario,
        clave,
        max_clients,
        max_upload_bytes,
        max_command_bytes,
        control_timeout,
        data_connect_timeout,
        data_timeout,
        max_login_attempts,
        pasv_address,
    })
}

// ---------------------------------------------------------------------------
// Comparación de credenciales de tiempo constante
// ---------------------------------------------------------------------------

/// Compara dos cadenas en tiempo constante respecto al contenido (no corta
/// en el primer byte distinto). Sí se adelanta si las longitudes difieren,
/// lo cual es inevitable sin relleno y no revela nada del contenido.
fn comparar_constante(a: &str, b: &str) -> bool {
    let (a, b) = (a.as_bytes(), b.as_bytes());
    if a.len() != b.len() {
        return false;
    }
    let mut diferencia = 0u8;
    for i in 0..a.len() {
        diferencia |= a[i] ^ b[i];
    }
    diferencia == 0
}

// ---------------------------------------------------------------------------
// Lector del canal de control
// ---------------------------------------------------------------------------

/// Lee una línea de comando del socket de control.
///
/// - Acepta terminación CRLF y LF.
/// - Conserva los bytes sobrantes del búfer (varios comandos juntos o un
///   comando fragmentado se procesan correctamente).
/// - Limita la línea a `max_bytes` (más CRLF); una línea mayor es una
///   violación de protocolo y devuelve `InvalidData` sin acumular más.
/// - EOF con o sin datos parciales devuelve `Ok(None)` (la sesión termina).
fn leer_linea(reader: &mut BufReader<TcpStream>, max_bytes: usize) -> io::Result<Option<String>> {
    let mut linea: Vec<u8> = Vec::new();
    loop {
        let (n, hay_fin_de_linea) = {
            let disponibles = reader.fill_buf()?;
            if disponibles.is_empty() {
                return Ok(None);
            }
            match disponibles.iter().position(|&b| b == b'\n') {
                Some(pos) => {
                    linea.extend_from_slice(&disponibles[..=pos]);
                    (pos + 1, true)
                }
                None => {
                    linea.extend_from_slice(disponibles);
                    (disponibles.len(), false)
                }
            }
        };
        reader.consume(n);
        // +2 por el CRLF final que aún puede llegar.
        if linea.len() > max_bytes + 2 {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "línea de comando demasiado larga",
            ));
        }
        if hay_fin_de_linea {
            while matches!(linea.last(), Some(b'\n') | Some(b'\r')) {
                linea.pop();
            }
            return Ok(Some(String::from_utf8_lossy(&linea).into_owned()));
        }
    }
}

// ---------------------------------------------------------------------------
// Formato PASV y utilidades de red
// ---------------------------------------------------------------------------

/// Convierte dirección IPv4 y puerto a formato PASV: (h1,h2,h3,h4,p1,p2).
fn format_pasv_addr(ip: Ipv4Addr, port: u16) -> String {
    let octets = ip.octets();
    let p1 = port / 256;
    let p2 = port % 256;
    format!(
        "{},{},{},{},{},{}",
        octets[0], octets[1], octets[2], octets[3], p1, p2
    )
}

/// Acepta la conexión de datos con un tiempo máximo acotado.
///
/// std no ofrece `poll`/`select` sobre un `TcpListener` ni un `accept` con
/// timeout, y cerrar el listener desde otro hilo no despierta un `accept`
/// bloqueado de forma portable. La solución portable es poner el listener en
/// modo nonblocking y sonearlo con un `sleep` corto hasta el deadline.
///
/// Comprueba además que la IP del cliente de datos coincide con la del
/// cliente de control (ambas conexiones salen del mismo cliente en las
/// topologías habituales, LAN o NAT con un único equipo detrás). Devuelve
/// el código FTP con el que responder si falla.
fn aceptar_canal_datos(
    listener: &TcpListener,
    connect_timeout: Duration,
    data_timeout: Duration,
    ip_control: Option<IpAddr>,
) -> Result<TcpStream, (u16, &'static str)> {
    listener
        .set_nonblocking(true)
        .map_err(|_| (425, "No se pudo preparar el canal de datos"))?;
    let inicio = Instant::now();
    loop {
        match listener.accept() {
            Ok((stream, addr)) => {
                if let Some(esperada) = ip_control {
                    if addr.ip() != esperada {
                        let _ = stream.shutdown(Shutdown::Both);
                        return Err((
                            425,
                            "La IP del canal de datos no coincide con la del canal de control",
                        ));
                    }
                }
                // Restaura el modo blocking e INDEPENDIZA los timeouts: el de
                // conexión rige el accept; el de datos rige la transferencia.
                if stream.set_nonblocking(false).is_err()
                    || stream.set_read_timeout(Some(data_timeout)).is_err()
                    || stream.set_write_timeout(Some(data_timeout)).is_err()
                {
                    let _ = stream.shutdown(Shutdown::Both);
                    return Err((425, "No se pudo configurar el canal de datos"));
                }
                return Ok(stream);
            }
            Err(e) if e.kind() == io::ErrorKind::WouldBlock => {
                if inicio.elapsed() >= connect_timeout {
                    return Err((426, "No llegó la conexión de datos a tiempo"));
                }
                thread::sleep(INTERVALO_ACEPTAR);
            }
            Err(_) => return Err((425, "Error aceptando la conexión de datos")),
        }
    }
}

// ---------------------------------------------------------------------------
// Resolución segura de rutas
// ---------------------------------------------------------------------------

/// Comprueba que un componente de ruta FTP es un nombre plano: ni "." ni ".."
/// (ya tratados antes) ni un prefijo de unidad como "C:", que en Windows
/// haría que `PathBuf::push` sustituyera la ruta base en vez de añadirse.
fn componente_seguro(componente: &str) -> bool {
    let mut iter = Path::new(componente).components();
    let unico_normal = matches!(iter.next(), Some(Component::Normal(_)));
    unico_normal && iter.next().is_none()
}

/// Resuelve un camino (posiblemente inexistente) canónicamente: si existe se
/// canóniza entero (siguiendo enlaces simbólicos); si no, se canóniza el
/// ancestro existente más profundo y se reenganchan los componentes que
/// quedan. `cwd` y `raiz` ya son canónicos.
fn canonicalizar_con_padre(destino: &Path) -> io::Result<PathBuf> {
    if let Ok(canon) = fs::canonicalize(destino) {
        return Ok(canon);
    }
    match destino.parent() {
        Some(padre) if !padre.as_os_str().is_empty() => {
            let canon_padre = canonicalizar_con_padre(padre)?;
            let nombre = destino.file_name().ok_or_else(|| {
                io::Error::new(io::ErrorKind::InvalidInput, "ruta sin nombre de archivo")
            })?;
            Ok(canon_padre.join(nombre))
        }
        _ => Err(io::Error::new(
            io::ErrorKind::NotFound,
            "no se pudo resolver la ruta",
        )),
    }
}

/// Resuelve una ruta FTP (relativa o absoluta) contra la raíz virtual "/".
///
/// - Las rutas absolutas ("...") se resuelven desde la raíz; las relativas,
///   desde el directorio actual (`cwd`), que siempre está dentro de la raíz.
/// - "." y ".." se procesan por componentes; ".." nunca sale de la raíz.
/// - Se normalizan separadores invertidos a "/" y se rechazan componentes
///   con prefijo de unidad ("C:") o caracteres nulos.
/// - El resultado se canóniza (sigue enlaces simbólicos) y se comprueba la
///   contención en la raíz por componentes. Los enlaces que apunten FUERA de
///   la raíz quedan bloqueados; los que apunten dentro se aceptan.
/// - Un destino inexistente NO es un error aquí: se devuelve la ruta resuelta
///   (el padre debe existir y estar contenido; lo comprueba el caller con
///   `validar_escritura`). Esto permite STOR sobre archivos nuevos.
fn resolver_ruta(cwd: &Path, raiz: &Path, arg: &str) -> Option<PathBuf> {
    let arg = arg.replace('\\', "/");
    let mut destino = if arg.starts_with('/') {
        PathBuf::from(raiz)
    } else {
        PathBuf::from(cwd)
    };
    for componente in arg.split('/') {
        match componente {
            "" | "." => {}
            ".." => {
                // ".." confinado: desde la raíz virtual no se sale nunca.
                if destino != raiz {
                    destino.pop();
                }
            }
            c if c.contains('\0') => return None,
            c if componente_seguro(c) => destino.push(c),
            _ => return None,
        }
    }
    let resuelto = canonicalizar_con_padre(&destino).ok()?;
    // starts_with compara por componentes completos: la raíz "/datos/ftp" no
    // contiene a "/datos/ftp_privado" (un startswith de cadenas sí lo haría).
    if resuelto.starts_with(raiz) {
        Some(resuelto)
    } else {
        None
    }
}

/// Comprueba que `ruta` (ya resuelta) es un archivo legible dentro de la raíz.
fn validar_lectura(ruta: &Path, raiz: &Path) -> bool {
    let Ok(meta) = fs::symlink_metadata(ruta) else {
        return false;
    };
    if meta.file_type().is_symlink() || !meta.is_file() {
        return false;
    }
    ruta.starts_with(raiz)
}

/// Comprueba que en `ruta` (ya resuelta) se puede publicar un archivo.
///
/// Rechaza directorios, enlaces simbólicos existentes (STOR no sustituye un
/// enlace: escribir a través de uno podría salirse de la raíz) y padres
/// inexistentes o fuera de la raíz. Best-effort frente a TOCTOU (ver
/// docstring del módulo).
fn validar_escritura(ruta: &Path, raiz: &Path) -> bool {
    let Some(padre) = ruta.parent() else {
        return false;
    };
    let Ok(meta_padre) = fs::symlink_metadata(padre) else {
        return false;
    };
    if meta_padre.file_type().is_symlink() || !meta_padre.is_dir() {
        return false;
    }
    if !padre.starts_with(raiz) || !ruta.starts_with(raiz) {
        return false;
    }
    match fs::symlink_metadata(ruta) {
        Ok(meta) => {
            if meta.file_type().is_symlink() {
                return false;
            }
            meta.is_file()
        }
        Err(e) if e.kind() == io::ErrorKind::NotFound => true,
        Err(_) => false,
    }
}

// ---------------------------------------------------------------------------
// Operaciones sobre el canal de datos
// ---------------------------------------------------------------------------

/// Neutraliza CR, LF y demás caracteres de control en un nombre de archivo
/// para que un listado no pueda falsificar registros.
fn sanitizar_nombre(nombre: &str) -> String {
    nombre
        .chars()
        .map(|c| if c.is_control() { '_' } else { c })
        .collect()
}

/// Envía un listado LIST estilo Unix por el socket de datos, con límite de
/// entradas y de tamaño total aplicados MIENTRAS se envía (no se acumula el
/// directorio completo en memoria). Clasifica cada entrada con
/// `symlink_metadata` (no sigue enlaces): los enlaces simbólicos se muestran
/// con tipo 'l' y tamaño 0.
fn enviar_listado(data: &mut TcpStream, dir: &Path) -> io::Result<()> {
    let entradas = fs::read_dir(dir)?;
    let mut entradas_enviadas = 0usize;
    let mut bytes_enviados = 0usize;
    for entrada in entradas {
        if entradas_enviadas >= MAX_ENTRADAS_LIST || bytes_enviados >= MAX_BYTES_LIST {
            break;
        }
        // Una entrada ilegible se omite; un fallo del iterador aborta la
        // transferencia (el caller responde 426, nunca 226).
        let entrada = entrada?;
        let meta = match fs::symlink_metadata(entrada.path()) {
            Ok(m) => m,
            Err(_) => continue,
        };
        let tipo = meta.file_type();
        let permisos = if tipo.is_symlink() {
            "lrwxrwxrwx"
        } else if tipo.is_dir() {
            "drwxr-xr-x"
        } else {
            "-rw-r--r--"
        };
        let nombre = sanitizar_nombre(&entrada.file_name().to_string_lossy());
        let tam = if tipo.is_file() { meta.len() } else { 0 };
        let linea = format!("{permisos} 1 owner group {tam} Jan  1 00:00 {nombre}\r\n");
        data.write_all(linea.as_bytes())?;
        bytes_enviados += linea.len();
        entradas_enviadas += 1;
    }
    Ok(())
}

/// Envía un archivo por el socket de datos (RETR) en bloques acotados.
fn enviar_archivo(data: &mut TcpStream, ruta: &Path) -> io::Result<()> {
    let mut archivo = File::open(ruta)?;
    let mut buf = [0u8; BLOQUE_DATOS];
    loop {
        let n = archivo.read(&mut buf)?;
        if n == 0 {
            break;
        }
        data.write_all(&buf[..n])?;
    }
    Ok(())
}

/// Error posible al recibir un archivo (STOR).
enum ErrorRecepcion {
    TamanoExcedido,
    Io(io::Error),
}

/// Recibe un archivo desde el socket de datos (STOR) en bloques acotados,
/// aplicando el límite de tamaño DURANTE la recepción.
fn recibir_archivo(data: &mut TcpStream, archivo: &mut File, max_bytes: u64) -> Result<(), ErrorRecepcion> {
    let mut buf = [0u8; BLOQUE_DATOS];
    let mut recibidos: u64 = 0;
    loop {
        let n = data.read(&mut buf).map_err(ErrorRecepcion::Io)?;
        if n == 0 {
            break;
        }
        recibidos += n as u64;
        if recibidos > max_bytes {
            return Err(ErrorRecepcion::TamanoExcedido);
        }
        archivo.write_all(&buf[..n]).map_err(ErrorRecepcion::Io)?;
    }
    Ok(())
}

/// Crea un archivo temporal único (creación exclusiva) en `dir`.
fn crear_temporal(dir: &Path) -> io::Result<(File, PathBuf)> {
    static CONTADOR: AtomicU64 = AtomicU64::new(0);
    let pid = std::process::id();
    for intento in 0..100u32 {
        let nanos = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0);
        let nombre = format!(
            ".ftp-tmp-{pid}-{nanos}-{}-{intento}",
            CONTADOR.fetch_add(1, Ordering::Relaxed)
        );
        let ruta = dir.join(nombre);
        match File::options().write(true).create_new(true).open(&ruta) {
            Ok(archivo) => return Ok((archivo, ruta)),
            Err(e) if e.kind() == io::ErrorKind::AlreadyExists => continue,
            Err(e) => return Err(e),
        }
    }
    Err(io::Error::new(
        io::ErrorKind::AlreadyExists,
        "no se pudo crear un nombre de temporal único",
    ))
}

// ---------------------------------------------------------------------------
// Sesión FTP
// ---------------------------------------------------------------------------

/// Maneja una sesión FTP en una conexión de control.
fn manejar_cliente(stream: TcpStream, cfg: &'static Config) -> io::Result<()> {
    let peer = stream.peer_addr().ok();
    let peer_ip = peer.map(|p| p.ip());
    println!("Nueva conexión desde {peer:?}");

    stream.set_read_timeout(Some(cfg.control_timeout))?;
    stream.set_write_timeout(Some(cfg.control_timeout))?;
    let mut reader = BufReader::new(stream.try_clone()?);
    let mut stream = stream;

    let mut logged_in = false;
    let mut cwd = cfg.root.clone();
    let mut ultimo_usuario: Option<String> = None;
    let mut intentos_fallidos: u32 = 0;
    let mut pasv_listener: Option<TcpListener> = None;

    enviar_respuesta(&mut stream, 220, "Servidor FTP listo (solo std)")?;

    loop {
        let linea = match leer_linea(&mut reader, cfg.max_command_bytes) {
            Ok(Some(l)) => l,
            Ok(None) => {
                println!("Cliente desconectado {peer:?}");
                break;
            }
            Err(e) if e.kind() == io::ErrorKind::InvalidData => {
                let _ = enviar_respuesta(&mut stream, 500, "Línea de comando demasiado larga");
                println!("Sesión {peer:?} cerrada por línea de comando demasiado larga");
                break;
            }
            Err(e) if es_timeout(&e) => {
                println!("Sesión {peer:?} cerrada por inactividad del canal de control");
                break;
            }
            Err(e) => return Err(e),
        };

        let mut partes = linea.splitn(2, ' ');
        let cmd = partes.next().unwrap_or("").to_uppercase();
        let arg = partes.next().map(str::trim).unwrap_or("");
        // Nunca se registra el argumento de PASS: es la contraseña.
        if cmd == "PASS" {
            println!("CMD \"PASS\" ARG \"***\"");
        } else {
            println!("CMD {cmd:?} ARG {arg:?}");
        }

        match cmd.as_str() {
            "USER" => {
                // Un USER nuevo restablece el estado de autenticación y
                // descarta cualquier canal de datos pendiente.
                ultimo_usuario = Some(arg.to_string());
                logged_in = false;
                pasv_listener = None;
                enviar_respuesta(&mut stream, 331, "Usuario OK, contraseña requerida")?;
            }
            "PASS" => {
                let Some(usuario) = ultimo_usuario.as_deref() else {
                    enviar_respuesta(&mut stream, 503, "Primero envíe USER")?;
                    continue;
                };
                if intentos_fallidos >= cfg.max_login_attempts {
                    println!("Cerrando sesión {peer:?} por exceso de intentos de login");
                    enviar_respuesta(&mut stream, 530, "Demasiados intentos fallidos")?;
                    break;
                }
                // Se comparan SIEMPRE las dos credenciales (sin cortocircuito
                // entre ellas) y con tiempo constante.
                let usuario_ok = comparar_constante(usuario, &cfg.usuario);
                let clave_ok = comparar_constante(arg, &cfg.clave);
                if usuario_ok & clave_ok {
                    logged_in = true;
                    intentos_fallidos = 0;
                    println!("Login correcto desde {peer:?}");
                    enviar_respuesta(&mut stream, 230, "Usuario conectado")?;
                } else {
                    logged_in = false;
                    ultimo_usuario = None;
                    intentos_fallidos += 1;
                    if intentos_fallidos >= cfg.max_login_attempts {
                        // Mismo mensaje para usuario y clave incorrectos: no
                        // se revela qué credencial falló.
                        println!(
                            "Cerrando sesión {peer:?}: agotados {intentos_fallidos} intentos de login"
                        );
                        enviar_respuesta(
                            &mut stream,
                            530,
                            "Credenciales incorrectas; demasiados intentos, sesión cerrada",
                        )?;
                        break;
                    }
                    enviar_respuesta(&mut stream, 530, "Credenciales incorrectas")?;
                }
            }
            "SYST" => {
                enviar_respuesta(&mut stream, 215, "UNIX Type: L8")?;
            }
            "TYPE" => {
                if arg.eq_ignore_ascii_case("I") {
                    enviar_respuesta(&mut stream, 200, "Modo binario")?;
                } else {
                    enviar_respuesta(&mut stream, 504, "Solo TYPE I soportado")?;
                }
            }
            "PWD" => {
                let rel = cwd.strip_prefix(&cfg.root).unwrap_or(Path::new(""));
                let mut mostrado = String::from("/");
                mostrado.push_str(&rel.to_string_lossy().replace('\\', "/"));
                // RFC 959: las comillas dobles de la ruta se duplican.
                let mostrado = mostrado.replace('"', "\"\"");
                enviar_respuesta(&mut stream, 257, &format!("\"{mostrado}\" es el directorio actual"))?;
            }
            "CWD" => {
                if !logged_in {
                    enviar_respuesta(&mut stream, 530, "No conectado")?;
                    continue;
                }
                match resolver_ruta(&cwd, &cfg.root, arg) {
                    Some(nuevo) if nuevo.is_dir() => {
                        cwd = nuevo;
                        enviar_respuesta(&mut stream, 250, "Directorio cambiado")?;
                    }
                    _ => enviar_respuesta(&mut stream, 550, "No se puede cambiar de directorio")?,
                }
            }
            "PASV" => {
                if !logged_in {
                    enviar_respuesta(&mut stream, 530, "No conectado")?;
                    continue;
                }
                // Un PASV nuevo cierra el listener pendiente anterior.
                pasv_listener = None;
                match TcpListener::bind((cfg.host, 0)) {
                    Ok(listener) => {
                        let local = listener.local_addr().map_err(|e| {
                            eprintln!("Error en PASV: {e}");
                            e
                        })?;
                        let pasv_str = format_pasv_addr(cfg.pasv_address, local.port());
                        enviar_respuesta(
                            &mut stream,
                            227,
                            &format!("Entrando en modo pasivo ({pasv_str})"),
                        )?;
                        pasv_listener = Some(listener);
                    }
                    Err(e) => {
                        eprintln!("No se pudo abrir puerto pasivo: {e}");
                        enviar_respuesta(&mut stream, 425, "No se pudo abrir puerto pasivo")?;
                    }
                }
            }
            "LIST" => {
                if !logged_in {
                    enviar_respuesta(&mut stream, 530, "No conectado")?;
                    continue;
                }
                // Sin canal de datos pendiente el error es 425, con
                // independencia de la ruta (coherente con RFC 959).
                let Some(listener) = tomar_pasv(&mut pasv_listener, &mut stream) else {
                    continue;
                };
                let objetivo = if arg.is_empty() {
                    Some(cwd.clone())
                } else {
                    resolver_ruta(&cwd, &cfg.root, arg)
                };
                let Some(objetivo) = objetivo.filter(|p| p.is_dir()) else {
                    // listener se descarta aquí: el canal pendiente muere.
                    enviar_respuesta(&mut stream, 550, "No se puede listar el directorio")?;
                    continue;
                };
                enviar_respuesta(&mut stream, 150, "Abriendo conexión de datos para LIST")?;
                let resultado = aceptar_canal_datos(&listener, cfg.data_connect_timeout, cfg.data_timeout, peer_ip)
                    .and_then(|mut data| {
                        enviar_listado(&mut data, &objetivo)
                            .map_err(|_| (426, "Conexión de datos fallida"))
                            .map(|()| data)
                    });
                match resultado {
                    Ok(data) => {
                        let _ = data.shutdown(Shutdown::Both);
                        enviar_respuesta(&mut stream, 226, "Transferencia completada")?;
                    }
                    Err((codigo, msg)) => {
                        enviar_respuesta(&mut stream, codigo, msg)?;
                    }
                }
            }
            "RETR" => {
                if !logged_in {
                    enviar_respuesta(&mut stream, 530, "No conectado")?;
                    continue;
                }
                let Some(listener) = tomar_pasv(&mut pasv_listener, &mut stream) else {
                    continue;
                };
                // La ruta y el tipo de archivo se validan ANTES del 150.
                let ruta = resolver_ruta(&cwd, &cfg.root, arg);
                let Some(ruta) = ruta.filter(|p| validar_lectura(p, &cfg.root)) else {
                    enviar_respuesta(&mut stream, 550, "Archivo no disponible")?;
                    continue;
                };
                enviar_respuesta(&mut stream, 150, "Abriendo conexión de datos para RETR")?;
                let resultado = aceptar_canal_datos(&listener, cfg.data_connect_timeout, cfg.data_timeout, peer_ip)
                    .and_then(|mut data| {
                        enviar_archivo(&mut data, &ruta)
                            .map_err(|_| (426, "Conexión de datos fallida"))
                            .map(|()| data)
                    });
                match resultado {
                    Ok(data) => {
                        let _ = data.shutdown(Shutdown::Both);
                        enviar_respuesta(&mut stream, 226, "Transferencia completada")?;
                    }
                    Err((codigo, msg)) => {
                        enviar_respuesta(&mut stream, codigo, msg)?;
                    }
                }
            }
            "STOR" => {
                if !logged_in {
                    enviar_respuesta(&mut stream, 530, "No conectado")?;
                    continue;
                }
                let Some(listener) = tomar_pasv(&mut pasv_listener, &mut stream) else {
                    continue;
                };
                // 1. Validación del destino y de su directorio padre ANTES
                //    del 150; si falla, el listener se descarta.
                let ruta = resolver_ruta(&cwd, &cfg.root, arg);
                let Some(ruta) = ruta.filter(|p| validar_escritura(p, &cfg.root)) else {
                    enviar_respuesta(&mut stream, 550, "Acceso denegado")?;
                    continue;
                };
                // 2. Temporal con creación exclusiva en el directorio de
                //    destino, ANTES del 150, para que un fallo de creación
                //    responda con 450 sin código contradictorio.
                let padre = ruta.parent().expect("validar_escritura garantiza padre");
                let (mut archivo, temporal) = match crear_temporal(padre) {
                    Ok(t) => t,
                    Err(e) => {
                        eprintln!("STOR: no se pudo crear temporal: {e}");
                        enviar_respuesta(&mut stream, 450, "No se pudo preparar la escritura")?;
                        continue;
                    }
                };
                enviar_respuesta(&mut stream, 150, "Abriendo conexión de datos para STOR")?;
                // 3-6. Recepción con límite, errores de E/S, sync y cierre.
                let recepcion = aceptar_canal_datos(&listener, cfg.data_connect_timeout, cfg.data_timeout, peer_ip)
                    .and_then(|mut data| {
                        recibir_archivo(&mut data, &mut archivo, cfg.max_upload_bytes)
                            .map_err(|e| match e {
                                ErrorRecepcion::TamanoExcedido => {
                                    (552, "Archivo excede el tamaño máximo permitido")
                                }
                                ErrorRecepcion::Io(e) => {
                                    eprintln!("STOR: error de recepción: {e}");
                                    (426, "Conexión de datos fallida")
                                }
                            })
                            .map(|()| data)
                    });
                let publicable = match recepcion {
                    Ok(data) => {
                        let _ = data.shutdown(Shutdown::Both);
                        // sync_all NO se ignora: un fallo de sincronización
                        // cancela la publicación (el archivo previo queda).
                        archivo.sync_all().map_err(|e| {
                            eprintln!("STOR: error de sync_all: {e}");
                            (450, "No se pudo sincronizar el archivo")
                        })
                    }
                    Err((codigo, msg)) => Err((codigo, msg)),
                };
                drop(archivo);
                match publicable {
                    Ok(()) => {
                        // 7. Reemplazo atómico en el mismo volumen (en
                        //    Windows, fs::rename reemplaza el destino).
                        match fs::rename(&temporal, &ruta) {
                            Ok(()) => {
                                enviar_respuesta(&mut stream, 226, "Transferencia completada")?;
                            }
                            Err(e) => {
                                eprintln!("STOR: no se pudo publicar el archivo: {e}");
                                let _ = fs::remove_file(&temporal);
                                enviar_respuesta(&mut stream, 450, "No se pudo guardar el archivo")?;
                            }
                        }
                    }
                    Err((codigo, msg)) => {
                        // 8. En cualquier error se limpia el temporal y el
                        //    archivo anterior queda intacto.
                        let _ = fs::remove_file(&temporal);
                        enviar_respuesta(&mut stream, codigo, msg)?;
                    }
                }
            }
            "NOOP" => {
                enviar_respuesta(&mut stream, 200, "OK")?;
            }
            "QUIT" => {
                enviar_respuesta(&mut stream, 221, "Adiós")?;
                break;
            }
            _ => {
                enviar_respuesta(&mut stream, 502, "Comando no implementado")?;
            }
        }
    }
    Ok(())
}

/// Devuelve el listener PASV pendiente o responde 425 si no lo hay.
fn tomar_pasv(pasv: &mut Option<TcpListener>, stream: &mut TcpStream) -> Option<TcpListener> {
    match pasv.take() {
        Some(l) => Some(l),
        None => {
            let _ = enviar_respuesta(stream, 425, "Use PASV primero");
            None
        }
    }
}

fn es_timeout(e: &io::Error) -> bool {
    matches!(e.kind(), io::ErrorKind::TimedOut | io::ErrorKind::WouldBlock)
}

fn enviar_respuesta(stream: &mut TcpStream, code: u16, message: &str) -> io::Result<()> {
    let line = format!("{code} {message}\r\n");
    stream.write_all(line.as_bytes())
}

// ---------------------------------------------------------------------------
// Arranque
// ---------------------------------------------------------------------------

/// Semáforo de sesiones simultáneas: se adquiere ANTES de lanzar el hilo, de
/// forma que un flood de conexiones no genera hilos. Es por proceso, no
/// global entre procesos, y un cliente no puede bloquear a los demás (si la
/// cifra está llena, se rechaza con 421 solo a quien llega de más).
struct SemaforoClientes {
    activos: AtomicU64,
    maximo: u64,
}

impl SemaforoClientes {
    fn new(maximo: u64) -> Self {
        Self {
            activos: AtomicU64::new(0),
            maximo,
        }
    }
    fn intentar_adquirir(&self) -> bool {
        loop {
            let actual = self.activos.load(Ordering::Relaxed);
            if actual >= self.maximo {
                return false;
            }
            if self
                .activos
                .compare_exchange_weak(actual, actual + 1, Ordering::Acquire, Ordering::Relaxed)
                .is_ok()
            {
                return true;
            }
        }
    }
    fn liberar(&self) {
        self.activos.fetch_sub(1, Ordering::Release);
    }
}

fn main() {
    let vars: HashMap<String, String> = std::env::vars().collect();
    let cfg = match validar_configuracion(&vars) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Error de configuración: {e}");
            std::process::exit(1);
        }
    };
    // Config vive durante todo el proceso: cada hilo de sesión recibe una
    // referencia. Se fuga deliberadamente una única vez.
    let cfg: &'static Config = Box::leak(Box::new(cfg));

    let listener = match TcpListener::bind((cfg.host, cfg.port)) {
        Ok(l) => l,
        Err(e) => {
            eprintln!("No se puede escuchar en {}:{}: {e}", cfg.host, cfg.port);
            std::process::exit(1);
        }
    };
    let puerto_real = listener.local_addr().map(|a| a.port()).unwrap_or(cfg.port);
    println!("Servidor FTP escuchando en {}:{}", cfg.host, puerto_real);
    println!("Raíz del FTP: {}", cfg.root.display());
    println!(
        "Límites: max_clients={} max_upload={} max_cmd={} control_timeout={}s data_connect_timeout={}s data_timeout={}s pasv={}",
        cfg.max_clients,
        cfg.max_upload_bytes,
        cfg.max_command_bytes,
        cfg.control_timeout.as_secs(),
        cfg.data_connect_timeout.as_secs(),
        cfg.data_timeout.as_secs(),
        cfg.pasv_address
    );

    let semaforo = Arc::new(SemaforoClientes::new(cfg.max_clients as u64));
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                if !semaforo.intentar_adquirir() {
                    let mut stream = stream;
                    let _ = enviar_respuesta(&mut stream, 421, "Demasiadas conexiones, cierre el servicio");
                    eprintln!("Conexión rechazada por límite de clientes");
                    continue;
                }
                let semaforo = Arc::clone(&semaforo);
                thread::spawn(move || {
                    if let Err(e) = manejar_cliente(stream, cfg) {
                        eprintln!("Error en sesión FTP: {e}");
                    }
                    semaforo.liberar();
                });
            }
            Err(e) => {
                eprintln!("Error aceptando conexión: {e}");
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Tests unitarios
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    fn vars_de_prueba() -> HashMap<String, String> {
        let mut vars = HashMap::new();
        vars.insert("FTP_USUARIO".to_string(), "juan".to_string());
        vars.insert("FTP_CLAVE".to_string(), "clave-secreta".to_string());
        vars
    }

    /// Devuelve el mensaje de error de una configuración rechazada (sin
    /// requerir Debug para Config, que contiene la contraseña).
    fn error_de_config(vars: &HashMap<String, String>) -> String {
        match validar_configuracion(vars) {
            Ok(_) => panic!("la configuración debería haber sido rechazada"),
            Err(e) => e,
        }
    }

    fn dir_temporal(nombre: &str) -> PathBuf {
        static CONTADOR: AtomicU64 = AtomicU64::new(0);
        let nanos = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0);
        let ruta = std::env::temp_dir().join(format!(
            "ftp-server-test-{nombre}-{}-{nanos}",
            CONTADOR.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir_all(&ruta).unwrap();
        fs::canonicalize(&ruta).unwrap()
    }

    /// Par de sockets conectados por loopback para probar `leer_linea`.
    fn par_de_sockets() -> (TcpStream, TcpStream) {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let addr = listener.local_addr().unwrap();
        let cliente = TcpStream::connect(addr).unwrap();
        let (servidor, _) = listener.accept().unwrap();
        (cliente, servidor)
    }

    #[test]
    fn test_format_pasv_addr_v4() {
        let ip = Ipv4Addr::new(127, 0, 0, 1);
        let formatted = format_pasv_addr(ip, 2121);
        assert_eq!(formatted, "127,0,0,1,8,73"); // 2121 / 256 = 8, 2121 % 256 = 73
    }

    #[test]
    fn test_format_pasv_addr_otro_puerto() {
        let ip = Ipv4Addr::new(192, 168, 1, 50);
        let formatted = format_pasv_addr(ip, 8080);
        assert_eq!(formatted, "192,168,1,50,31,144"); // 8080 / 256 = 31, 8080 % 256 = 144
    }

    #[test]
    fn comparar_constante_acepta_iguales() {
        assert!(comparar_constante("clave-secreta", "clave-secreta"));
        assert!(comparar_constante("", ""));
    }

    #[test]
    fn comparar_constante_rechaza_distintas_y_longitud() {
        assert!(!comparar_constante("clave-secreta", "clave-secretb"));
        assert!(!comparar_constante("corta", "clave-larga"));
        assert!(!comparar_constante("", "x"));
    }

    #[test]
    fn configuracion_valida_con_predeterminados() {
        let vars = vars_de_prueba();
        let cfg = validar_configuracion(&vars).unwrap();
        assert_eq!(cfg.host, Ipv4Addr::new(127, 0, 0, 1));
        assert_eq!(cfg.port, 2121);
        assert_eq!(cfg.max_clients, 10);
        assert_eq!(cfg.max_upload_bytes, 50 * 1024 * 1024);
        assert_eq!(cfg.max_command_bytes, 8192);
        assert_eq!(cfg.max_login_attempts, 3);
        assert_eq!(cfg.pasv_address, Ipv4Addr::new(127, 0, 0, 1));
        // La raíz predeterminada queda junto al binario de test, no en el CWD.
        assert!(cfg.root.ends_with("storage"));
    }

    #[test]
    fn configuracion_rechaza_puerto_fuera_de_rango() {
        let mut vars = vars_de_prueba();
        vars.insert("FTP_PORT".to_string(), "99999".to_string());
        let e = error_de_config(&vars);
        assert!(e.contains("FTP_PORT"), "mensaje: {e}");
        vars.insert("FTP_PORT".to_string(), "abc".to_string());
        assert!(validar_configuracion(&vars).is_err());
    }

    #[test]
    fn configuracion_rechaza_credenciales_faltantes() {
        let vars = HashMap::new();
        let e = error_de_config(&vars);
        assert!(e.contains("FTP_USUARIO"), "mensaje: {e}");
        let mut vars = vars_de_prueba();
        vars.remove("FTP_CLAVE");
        let e = error_de_config(&vars);
        assert!(e.contains("FTP_CLAVE"), "mensaje: {e}");
    }

    #[test]
    fn configuracion_rechaza_max_clients_cero_y_upload_negativo() {
        let mut vars = vars_de_prueba();
        vars.insert("FTP_MAX_CLIENTS".to_string(), "0".to_string());
        assert!(validar_configuracion(&vars).is_err());
        let mut vars = vars_de_prueba();
        vars.insert("FTP_MAX_UPLOAD_BYTES".to_string(), "-5".to_string());
        assert!(validar_configuracion(&vars).is_err());
    }

    #[test]
    fn configuracion_rechaza_host_no_ipv4() {
        let mut vars = vars_de_prueba();
        vars.insert("FTP_HOST".to_string(), "localhost".to_string());
        let e = error_de_config(&vars);
        assert!(e.contains("FTP_HOST"), "mensaje: {e}");
    }

    #[test]
    fn configuracion_rechaza_pasv_address_en_blanco_invalida_o_cero() {
        let mut vars = vars_de_prueba();
        vars.insert("FTP_HOST".to_string(), "0.0.0.0".to_string());
        let e = error_de_config(&vars);
        assert!(e.contains("FTP_PASV_ADDRESS"), "mensaje: {e}");
        vars.insert("FTP_PASV_ADDRESS".to_string(), "0.0.0.0".to_string());
        let e = error_de_config(&vars);
        assert!(e.contains("0.0.0.0"), "mensaje: {e}");
        vars.insert("FTP_PASV_ADDRESS".to_string(), "no-es-ip".to_string());
        assert!(validar_configuracion(&vars).is_err());
    }

    #[test]
    fn raiz_se_crea_y_queda_canonica() {
        let base = dir_temporal("raiz");
        let destino = base.join("hija").join("nieto");
        assert!(!destino.exists());
        let raiz = preparar_raiz(&destino).unwrap();
        assert!(raiz.is_dir());
        assert_eq!(raiz, fs::canonicalize(&raiz).unwrap());
        fs::remove_dir_all(&base).unwrap();
    }

    #[test]
    fn resolver_ruta_relativa_y_absoluta() {
        let raiz = dir_temporal("resolver");
        fs::create_dir_all(raiz.join("sub")).unwrap();
        let cwd = raiz.clone();
        let relativa = resolver_ruta(&cwd, &raiz, "sub").unwrap();
        assert_eq!(relativa, raiz.join("sub"));
        let absoluta = resolver_ruta(&cwd, &raiz, "/sub").unwrap();
        assert_eq!(absoluta, raiz.join("sub"));
        let vacia = resolver_ruta(&cwd, &raiz, "").unwrap();
        assert_eq!(vacia, raiz);
        fs::remove_dir_all(&raiz).unwrap();
    }

    #[test]
    fn resolver_ruta_procesa_puntos_y_puntos_dobles_sin_escapar() {
        let raiz = dir_temporal("puntos");
        fs::create_dir_all(raiz.join("a").join("b")).unwrap();
        let cwd = raiz.join("a").join("b");
        // ".." confinado en la raíz.
        let sube = resolver_ruta(&cwd, &raiz, "../..").unwrap();
        assert_eq!(sube, raiz);
        let sale = resolver_ruta(&cwd, &raiz, "../../..").unwrap();
        assert_eq!(sale, raiz, "'..' desde la raíz no debe salir");
        // "/../sub": el ".." inicial se confina en la raíz y "sub" cuelga de ella.
        let mezcla = resolver_ruta(&cwd, &raiz, "/../sub").unwrap();
        assert_eq!(mezcla, raiz.join("sub"));
        let con_punto = resolver_ruta(&cwd, &raiz, "./x/./y").unwrap();
        assert_eq!(con_punto, cwd.join("x").join("y"));
        fs::remove_dir_all(&raiz).unwrap();
    }

    #[test]
    fn resolver_ruta_normaliza_separadores_invertidos() {
        let raiz = dir_temporal("separadores");
        fs::create_dir_all(raiz.join("a").join("b")).unwrap();
        let cwd = raiz.clone();
        let ruta = resolver_ruta(&cwd, &raiz, "a\\b").unwrap();
        assert_eq!(ruta, raiz.join("a").join("b"));
        fs::remove_dir_all(&raiz).unwrap();
    }

    #[cfg(windows)]
    #[test]
    fn resolver_ruta_rechaza_prefijo_de_unidad_en_windows() {
        let raiz = dir_temporal("unidad");
        let cwd = raiz.clone();
        assert!(resolver_ruta(&cwd, &raiz, "C:/windows/system32").is_none());
        assert!(resolver_ruta(&cwd, &raiz, "C:algo").is_none());
        fs::remove_dir_all(&raiz).unwrap();
    }

    #[cfg(unix)]
    #[test]
    fn resolver_ruta_trata_los_dos_puntos_como_nombre_en_unix() {
        // En Unix "C:" es un nombre de archivo corriente (sin prefijo de
        // unidad): la política es rechazar solo lo que `Component` detecta
        // como prefijo, y el resultado debe quedar dentro de la raíz.
        let raiz = dir_temporal("unidad");
        let cwd = raiz.clone();
        let ruta = resolver_ruta(&cwd, &raiz, "C:/windows").unwrap();
        assert!(ruta.starts_with(&raiz));
        fs::remove_dir_all(&raiz).unwrap();
    }

    #[test]
    fn resolver_ruta_con_componente_nulo_rechazada() {
        let raiz = dir_temporal("nulo");
        let cwd = raiz.clone();
        assert!(resolver_ruta(&cwd, &raiz, "a\0b").is_none());
        fs::remove_dir_all(&raiz).unwrap();
    }

    #[test]
    fn resolver_ruta_inexistente_sigue_valida_para_stor() {
        let raiz = dir_temporal("inexistente");
        let cwd = raiz.clone();
        let destino = resolver_ruta(&cwd, &raiz, "nuevo/archivo.txt").unwrap();
        assert_eq!(destino, raiz.join("nuevo").join("archivo.txt"));
        // Pero validar_escritura la rechaza: el padre no existe.
        assert!(!validar_escritura(&destino, &raiz));
        fs::create_dir_all(raiz.join("nuevo")).unwrap();
        assert!(validar_escritura(&destino, &raiz));
        fs::remove_dir_all(&raiz).unwrap();
    }

    #[test]
    fn validar_lectura_rechaza_directorios_y_faltantes() {
        let raiz = dir_temporal("lectura");
        fs::write(raiz.join("f.txt"), b"hola").unwrap();
        assert!(validar_lectura(&raiz.join("f.txt"), &raiz));
        assert!(!validar_lectura(&raiz, &raiz));
        assert!(!validar_lectura(&raiz.join("no-existe.txt"), &raiz));
        fs::remove_dir_all(&raiz).unwrap();
    }

    #[cfg(unix)]
    #[test]
    fn enlace_simbolico_hacia_fuera_de_la_raiz_se_rechaza() {
        let raiz = dir_temporal("symlink-raiz");
        let fuera = dir_temporal("symlink-fuera");
        fs::write(fuera.join("secreto.txt"), b"secreto").unwrap();
        std::os::unix::fs::symlink(&fuera, raiz.join("enlace")).unwrap();
        let cwd = raiz.clone();
        // RETR a través del enlace: resuelve fuera de la raíz → rechazado.
        assert!(resolver_ruta(&cwd, &raiz, "enlace/secreto.txt").is_none());
        assert!(resolver_ruta(&cwd, &raiz, "enlace").is_none());
        fs::remove_dir_all(&raiz).unwrap();
        fs::remove_dir_all(&fuera).unwrap();
    }

    #[cfg(windows)]
    #[test]
    fn enlace_simbolico_hacia_fuera_de_la_raiz_se_rechaza_en_windows() {
        let raiz = dir_temporal("symlink-raiz");
        let fuera = dir_temporal("symlink-fuera");
        fs::write(fuera.join("secreto.txt"), b"secreto").unwrap();
        // Crear enlaces simbólicos en Windows exige privilegios o modo
        // desarrollador: si no se puede, el test queda sin validar.
        if std::os::windows::fs::symlink_file(fuera.join("secreto.txt"), raiz.join("enlace.txt"))
            .is_err()
        {
            eprintln!("aviso: sin privilegios para crear symlinks, test omitido");
            fs::remove_dir_all(&raiz).unwrap();
            fs::remove_dir_all(&fuera).unwrap();
            return;
        }
        let cwd = raiz.clone();
        assert!(resolver_ruta(&cwd, &raiz, "enlace.txt").is_none());
        fs::remove_dir_all(&raiz).unwrap();
        fs::remove_dir_all(&fuera).unwrap();
    }

    #[test]
    fn sanitizar_nombre_neutraliza_caracteres_de_control() {
        assert_eq!(sanitizar_nombre("normal.txt"), "normal.txt");
        assert_eq!(sanitizar_nombre("mal\n\r nombre"), "mal__ nombre");
        assert_eq!(sanitizar_nombre("tab\tx"), "tab_x");
        assert_eq!(sanitizar_nombre("del\x7fx"), "del_x");
    }

    #[test]
    fn leer_linea_acepta_crlf_y_lf() {
        let (mut cliente, servidor) = par_de_sockets();
        let mut reader = BufReader::new(servidor);
        cliente.write_all(b"USER juan\r\nPASS clave\nNOOP\r\n").unwrap();
        assert_eq!(leer_linea(&mut reader, 100).unwrap(), Some("USER juan".into()));
        assert_eq!(leer_linea(&mut reader, 100).unwrap(), Some("PASS clave".into()));
        assert_eq!(leer_linea(&mut reader, 100).unwrap(), Some("NOOP".into()));
    }

    #[test]
    fn leer_linea_conserva_fragmentos_y_comandos_juntos() {
        let (mut cliente, servidor) = par_de_sockets();
        let mut reader = BufReader::new(servidor);
        cliente.write_all(b"USER ju").unwrap();
        cliente.write_all(b"an\r\nNOOP").unwrap();
        assert_eq!(leer_linea(&mut reader, 100).unwrap(), Some("USER juan".into()));
        // NOOP sin CRLF aún: no devuelve nada hasta que llegue el fin de línea.
        cliente.write_all(b"\r\n").unwrap();
        assert_eq!(leer_linea(&mut reader, 100).unwrap(), Some("NOOP".into()));
    }

    #[test]
    fn leer_linea_falla_si_excede_el_maximo() {
        let (mut cliente, servidor) = par_de_sockets();
        let mut reader = BufReader::new(servidor);
        let larga = "X".repeat(200);
        cliente.write_all(format!("{larga}\r\n").as_bytes()).unwrap();
        let e = leer_linea(&mut reader, 64).unwrap_err();
        assert_eq!(e.kind(), io::ErrorKind::InvalidData);
    }

    #[test]
    fn leer_linea_devuelve_none_en_eof() {
        let (cliente, servidor) = par_de_sockets();
        let mut reader = BufReader::new(servidor);
        drop(cliente);
        assert_eq!(leer_linea(&mut reader, 100).unwrap(), None);
    }

    #[test]
    fn crear_temporal_usa_creacion_exclusiva() {
        let dir = dir_temporal("temporales");
        let (f1, ruta1) = crear_temporal(&dir).unwrap();
        let (_f2, ruta2) = crear_temporal(&dir).unwrap();
        drop(f1);
        assert_ne!(ruta1, ruta2);
        assert!(ruta1.is_file());
        // No se puede crear dos veces el mismo nombre.
        let e = File::options()
            .write(true)
            .create_new(true)
            .open(&ruta1)
            .unwrap_err();
        assert_eq!(e.kind(), io::ErrorKind::AlreadyExists);
        fs::remove_dir_all(&dir).unwrap();
    }

    #[test]
    fn semaforo_de_clientes_limita_sin_bloquear() {
        let s = SemaforoClientes::new(2);
        assert!(s.intentar_adquirir());
        assert!(s.intentar_adquirir());
        assert!(!s.intentar_adquirir(), "el tercer cliente debe rechazarse");
        s.liberar();
        assert!(s.intentar_adquirir());
    }
}

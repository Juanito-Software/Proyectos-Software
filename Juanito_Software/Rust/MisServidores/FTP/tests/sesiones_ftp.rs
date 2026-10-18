//! Pruebas de integración del servidor FTP: arrancan el binario real con
//! configuración por variables de entorno y hablan el protocolo por el
//! canal de control (cliente mínimo implementado con std).

use std::fs;
use std::io::{BufRead, BufReader, Read, Write};
use std::net::TcpStream;
use std::path::PathBuf;
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

const USUARIO: &str = "juan";
const CLAVE: &str = "clave-secreta";

// ---------------------------------------------------------------------------
// Infraestructura de pruebas
// ---------------------------------------------------------------------------

/// Servidor real en proceso, con raíz temporal y puerto efímero.
struct ServidorDePrueba {
    hijo: Child,
    puerto: u16,
    raiz: PathBuf,
}

fn dir_temporal() -> PathBuf {
    static CONTADOR: AtomicU64 = AtomicU64::new(0);
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    let ruta = std::env::temp_dir().join(format!(
        "ftp-server-int-{}-{nanos}",
        CONTADOR.fetch_add(1, Ordering::Relaxed)
    ));
    fs::create_dir_all(&ruta).unwrap();
    fs::canonicalize(&ruta).unwrap()
}

impl ServidorDePrueba {
    /// Arranca el binario con la configuración base y devuelve el puerto
    /// efímero real que anuncia en el log.
    fn arrancar(extra: &[(&str, &str)]) -> ServidorDePrueba {
        let raiz = dir_temporal();
        let mut cmd = Command::new(env!("CARGO_BIN_EXE_ftp_server"));
        cmd.env("FTP_HOST", "127.0.0.1")
            .env("FTP_PORT", "0")
            .env("FTP_ROOT", &raiz)
            .env("FTP_USUARIO", USUARIO)
            .env("FTP_CLAVE", CLAVE)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        for (clave, valor) in extra {
            cmd.env(clave, valor);
        }
        let mut hijo = cmd.spawn().expect("no se pudo arrancar el servidor");
        let stdout = hijo.stdout.take().unwrap();
        let stderr = hijo.stderr.take().unwrap();
        // Drenar stderr para que el pipe no se llene y bloquee al servidor.
        thread::spawn(move || {
            let mut basura = Vec::new();
            let _ = BufReader::new(stderr).read_to_end(&mut basura);
        });
        let mut reader = BufReader::new(stdout);
        let puerto = loop {
            let mut linea = String::new();
            let n = reader.read_line(&mut linea).expect("stdout ilegible");
            assert!(n > 0, "el servidor terminó antes de anunciar el puerto: {linea}");
            if let Some(resto) = linea.split("escuchando en 127.0.0.1:").nth(1) {
                break resto
                    .trim()
                    .parse::<u16>()
                    .expect("el puerto anunciado no es un número");
            }
        };
        // El resto del stdout se drena en un hilo por el mismo motivo.
        thread::spawn(move || {
            let mut basura = Vec::new();
            let _ = reader.read_to_end(&mut basura);
        });
        ServidorDePrueba { hijo, puerto, raiz }
    }
}

impl Drop for ServidorDePrueba {
    fn drop(&mut self) {
        let _ = self.hijo.kill();
        let _ = self.hijo.wait();
        let _ = fs::remove_dir_all(&self.raiz);
    }
}

/// Cliente FTP mínimo sobre el canal de control.
struct Cliente {
    stream: TcpStream,
    reader: BufReader<TcpStream>,
}

impl Cliente {
    fn conectar(puerto: u16) -> Cliente {
        let stream = TcpStream::connect(("127.0.0.1", puerto)).expect("conexión rechazada");
        configurar_timeouts(&stream);
        let reader = BufReader::new(stream.try_clone().unwrap());
        let mut cliente = Cliente { stream, reader };
        let bienvenida = cliente.respuesta();
        assert!(bienvenida.starts_with("220 "), "bienvenida: {bienvenida}");
        cliente
    }

    fn enviar(&mut self, linea: &str) {
        self.stream
            .write_all(format!("{linea}\r\n").as_bytes())
            .expect("no se pudo enviar el comando");
    }

    fn enviar_crudo(&mut self, datos: &[u8]) {
        self.stream.write_all(datos).expect("no se pudo enviar datos");
    }

    /// Lee una respuesta; paniquea si el servidor cierra antes de enviarla.
    fn respuesta(&mut self) -> String {
        self.respuesta_opcional()
            .expect("el servidor cerró la conexión sin responder")
    }

    fn respuesta_opcional(&mut self) -> Option<String> {
        let mut linea = String::new();
        let n = self.reader.read_line(&mut linea).unwrap();
        if n == 0 {
            None
        } else {
            Some(linea.trim_end().to_string())
        }
    }

    fn login(&mut self) {
        self.enviar(&format!("USER {USUARIO}"));
        assert!(self.respuesta().starts_with("331 "));
        self.enviar(&format!("PASS {CLAVE}"));
        assert!(self.respuesta().starts_with("230 "));
    }

    /// Ejecuta PASV y devuelve el puerto anunciado.
    fn puerto_pasv(&mut self) -> u16 {
        self.enviar("PASV");
        let r = self.respuesta();
        assert!(r.starts_with("227 "), "respuesta a PASV: {r}");
        let inicio = r.find('(').expect("227 sin paréntesis de apertura") + 1;
        let fin = r.find(')').expect("227 sin paréntesis de cierre");
        let partes: Vec<u16> = r[inicio..fin]
            .split(',')
            .map(|p| p.trim().parse().expect("octeto ilegible en 227"))
            .collect();
        assert_eq!(partes.len(), 6, "227 con menos de 6 campos: {r}");
        partes[4] * 256 + partes[5]
    }

    fn conectar_datos(&self, puerto_pasv: u16) -> TcpStream {
        let s = TcpStream::connect(("127.0.0.1", puerto_pasv)).expect("canal de datos rechazado");
        configurar_timeouts(&s);
        s
    }
}

fn configurar_timeouts(stream: &TcpStream) {
    stream.set_read_timeout(Some(Duration::from_secs(10))).unwrap();
    stream.set_write_timeout(Some(Duration::from_secs(10))).unwrap();
}

/// Deja un socket de datos abierto y a medias: el servidor debe agotar
/// FTP_DATA_TIMEOUT y abortar la transferencia (no puede ser un EOF limpio,
/// que equivaldría a un STOR válido).
fn transferencia_abierta_sin_cerrar(datos: &TcpStream) {
    let _ = datos.set_read_timeout(Some(Duration::from_secs(10)));
}

fn temporales_en(dir: &PathBuf) -> Vec<PathBuf> {
    fs::read_dir(dir)
        .unwrap()
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| {
            p.file_name()
                .and_then(|n| n.to_str())
                .is_some_and(|n| n.starts_with(".ftp-tmp-"))
        })
        .collect()
}

// ---------------------------------------------------------------------------
// Arranque y configuración
// ---------------------------------------------------------------------------

#[test]
fn arranca_y_responde_con_bienvenida_220() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let _cliente = Cliente::conectar(servidor.puerto);
}

#[test]
fn sin_credenciales_el_servidor_no_arranca() {
    let raiz = dir_temporal();
    let salida = Command::new(env!("CARGO_BIN_EXE_ftp_server"))
        .env("FTP_HOST", "127.0.0.1")
        .env("FTP_PORT", "0")
        .env("FTP_ROOT", &raiz)
        .output()
        .expect("no se pudo lanzar el binario");
    assert!(!salida.status.success(), "el servidor debe salir con error");
    let stderr = String::from_utf8_lossy(&salida.stderr);
    assert!(stderr.contains("FTP_USUARIO"), "stderr: {stderr}");
    let _ = fs::remove_dir_all(&raiz);
}

#[test]
fn host_no_ipv4_no_arranca() {
    let raiz = dir_temporal();
    let salida = Command::new(env!("CARGO_BIN_EXE_ftp_server"))
        .env("FTP_HOST", "::1")
        .env("FTP_PORT", "0")
        .env("FTP_ROOT", &raiz)
        .env("FTP_USUARIO", USUARIO)
        .env("FTP_CLAVE", CLAVE)
        .output()
        .expect("no se pudo lanzar el binario");
    assert!(!salida.status.success());
    let stderr = String::from_utf8_lossy(&salida.stderr);
    assert!(stderr.contains("IPv4"), "stderr: {stderr}");
    let _ = fs::remove_dir_all(&raiz);
}

#[test]
fn pasv_anuncia_la_direccion_configurada() {
    let servidor = ServidorDePrueba::arrancar(&[("FTP_PASV_ADDRESS", "192.168.50.9")]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    cliente.enviar("PASV");
    let r = cliente.respuesta();
    assert!(r.starts_with("227 "), "respuesta: {r}");
    assert!(r.contains("192,168,50,9"), "debe anunciarse FTP_PASV_ADDRESS: {r}");
}

// ---------------------------------------------------------------------------
// Autenticación y estado de sesión
// ---------------------------------------------------------------------------

#[test]
fn pass_sin_user_responde_503() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.enviar(&format!("PASS {CLAVE}"));
    assert!(cliente.respuesta().starts_with("503 "));
}

#[test]
fn pass_incorrecto_no_autentica_y_las_operaciones_piden_login() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.enviar("USER juan");
    assert!(cliente.respuesta().starts_with("331 "));
    cliente.enviar("PASS incorrecta");
    let r = cliente.respuesta();
    assert!(r.starts_with("530 "), "respuesta: {r}");
    cliente.enviar("CWD /");
    assert!(cliente.respuesta().starts_with("530 "));
    cliente.enviar("LIST");
    assert!(cliente.respuesta().starts_with("530 "));
    cliente.enviar("STOR x.txt");
    assert!(cliente.respuesta().starts_with("530 "));
}

#[test]
fn limite_de_intentos_de_login_cierra_la_sesion() {
    let servidor = ServidorDePrueba::arrancar(&[("FTP_MAX_LOGIN_ATTEMPTS", "2")]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    for (intento, clave) in [(1, "mala-1"), (2, "mala-2")] {
        cliente.enviar("USER juan");
        assert!(cliente.respuesta().starts_with("331 "), "intento {intento}");
        cliente.enviar(&format!("PASS {clave}"));
        let r = cliente.respuesta();
        assert!(r.starts_with("530 "), "intento {intento}: {r}");
    }
    // Con los intentos agotados la sesión se cierra: no hay más respuestas.
    assert_eq!(cliente.respuesta_opcional(), None, "la sesión debe cerrarse");
}

#[test]
fn pass_sin_user_no_elude_el_limite_de_intentos() {
    let servidor = ServidorDePrueba::arrancar(&[("FTP_MAX_LOGIN_ATTEMPTS", "1")]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    // PASS sin USER responde 503 y no cuenta como intento.
    cliente.enviar("PASS mala");
    assert!(cliente.respuesta().starts_with("503 "));
    // El único intento permitido se consume con la primera PASS con USER.
    cliente.enviar("USER juan");
    assert!(cliente.respuesta().starts_with("331 "));
    cliente.enviar("PASS mala");
    assert!(cliente.respuesta().starts_with("530 "));
    assert_eq!(cliente.respuesta_opcional(), None, "la sesión debe cerrarse");
}

#[test]
fn login_correcto_permite_pwd() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    cliente.enviar("PWD");
    let r = cliente.respuesta();
    assert!(r.starts_with("257 "), "PWD: {r}");
    assert!(r.contains("\"/\""), "la raíz virtual es '/': {r}");
}

#[test]
fn user_nuevo_deja_la_sesion_sin_autenticar() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    cliente.enviar("USER otro");
    assert!(cliente.respuesta().starts_with("331 "));
    cliente.enviar("RETR cualquier-cosa.txt");
    assert!(
        cliente.respuesta().starts_with("530 "),
        "tras un USER nuevo debe exigirse autenticación de nuevo"
    );
}

// ---------------------------------------------------------------------------
// Resolución de rutas y CWD
// ---------------------------------------------------------------------------

#[test]
fn cwd_confina_en_la_raiz() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    fs::create_dir_all(servidor.raiz.join("sub")).unwrap();
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();

    cliente.enviar("CWD sub");
    assert!(cliente.respuesta().starts_with("250 "));
    cliente.enviar("PWD");
    assert!(cliente.respuesta().contains("\"/sub\""));

    // ".." desde sub vuelve a la raíz.
    cliente.enviar("CWD ..");
    assert!(cliente.respuesta().starts_with("250 "));
    cliente.enviar("PWD");
    assert!(cliente.respuesta().contains("\"/\""));

    // ".." desde la raíz NO sale: sigue respondiendo 250 y PWD es "/".
    cliente.enviar("CWD ..");
    assert!(cliente.respuesta().starts_with("250 "));
    cliente.enviar("PWD");
    assert!(cliente.respuesta().contains("\"/\""));

    // Ruta absoluta con .. confinada.
    cliente.enviar("CWD /../..");
    assert!(cliente.respuesta().starts_with("250 "));
    cliente.enviar("PWD");
    assert!(cliente.respuesta().contains("\"/\""));
}

#[test]
fn retr_de_ruta_fuera_de_la_raiz_se_rechaza() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    fs::write(servidor.raiz.join("dentro.txt"), b"contenido").unwrap();
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    // Cada RETR lleva su PASV: el rechazo debe ser por la ruta, no por 425.
    let _pd = cliente.puerto_pasv();
    cliente.enviar("RETR ../../fuera.txt");
    assert!(cliente.respuesta().starts_with("550 "));
    let _pd = cliente.puerto_pasv();
    cliente.enviar("RETR /../../etc/passwd");
    assert!(cliente.respuesta().starts_with("550 "));
    // Una ruta válida pero inexistente también es 550 (antes del 150).
    let _pd = cliente.puerto_pasv();
    cliente.enviar("RETR no-existe.txt");
    assert!(cliente.respuesta().starts_with("550 "));
}

#[cfg(unix)]
#[test]
fn retr_a_traves_de_enlace_simbolico_fuera_de_la_raiz_se_rechaza() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let fuera = dir_temporal();
    fs::write(fuera.join("secreto.txt"), b"secreto").unwrap();
    std::os::unix::fs::symlink(fuera.join("secreto.txt"), servidor.raiz.join("enlace.txt")).unwrap();
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    let _pd = cliente.puerto_pasv();
    cliente.enviar("RETR enlace.txt");
    assert!(cliente.respuesta().starts_with("550 "));
    let _ = fs::remove_dir_all(&fuera);
}

#[cfg(windows)]
#[test]
fn retr_a_traves_de_enlace_simbolico_fuera_de_la_raiz_se_rechaza_en_windows() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let fuera = dir_temporal();
    fs::write(fuera.join("secreto.txt"), b"secreto").unwrap();
    if std::os::windows::fs::symlink_file(fuera.join("secreto.txt"), servidor.raiz.join("enlace.txt"))
        .is_err()
    {
        eprintln!("aviso: sin privilegios para crear symlinks, test omitido");
        let _ = fs::remove_dir_all(&fuera);
        return;
    }
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    let _pd = cliente.puerto_pasv();
    cliente.enviar("RETR enlace.txt");
    assert!(cliente.respuesta().starts_with("550 "));
    let _ = fs::remove_dir_all(&fuera);
}

// ---------------------------------------------------------------------------
// LIST
// ---------------------------------------------------------------------------

#[test]
fn list_de_directorio_vacio_devuelve_226_sin_contenido() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    let puerto_datos = cliente.puerto_pasv();
    cliente.enviar("LIST");
    assert!(cliente.respuesta().starts_with("150 "));
    let mut datos = cliente.conectar_datos(puerto_datos);
    let mut listado = Vec::new();
    datos.read_to_end(&mut listado).unwrap();
    datos.shutdown(std::net::Shutdown::Both).unwrap();
    assert!(listado.is_empty(), "un directorio vacío no lista nada: {listado:?}");
    assert!(cliente.respuesta().starts_with("226 "));
}

#[test]
fn list_incluye_los_archivos_del_directorio() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    fs::write(servidor.raiz.join("hola.txt"), b"hola").unwrap();
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    let puerto_datos = cliente.puerto_pasv();
    cliente.enviar("LIST");
    assert!(cliente.respuesta().starts_with("150 "));
    let mut datos = cliente.conectar_datos(puerto_datos);
    let mut listado = Vec::new();
    datos.read_to_end(&mut listado).unwrap();
    datos.shutdown(std::net::Shutdown::Both).unwrap();
    let listado = String::from_utf8_lossy(&listado);
    assert!(listado.contains("hola.txt"), "listado: {listado}");
    assert!(cliente.respuesta().starts_with("226 "));
}

// ---------------------------------------------------------------------------
// RETR y STOR
// ---------------------------------------------------------------------------

#[test]
fn stor_y_retr_transfieren_un_archivo_grande_completo() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();

    // 200 KiB para ejercitar la transferencia por bloques (64 KiB).
    let contenido: Vec<u8> = (0..200 * 1024).map(|i| (i % 256) as u8).collect();
    let puerto_datos = cliente.puerto_pasv();
    cliente.enviar("STOR grande.bin");
    assert!(cliente.respuesta().starts_with("150 "));
    let mut datos = cliente.conectar_datos(puerto_datos);
    datos.write_all(&contenido).unwrap();
    datos.shutdown(std::net::Shutdown::Write).unwrap();
    drop(datos);
    assert!(cliente.respuesta().starts_with("226 "), "STOR debe completarse");

    let puerto_datos = cliente.puerto_pasv();
    cliente.enviar("RETR grande.bin");
    assert!(cliente.respuesta().starts_with("150 "));
    let mut datos = cliente.conectar_datos(puerto_datos);
    let mut recibido = Vec::new();
    datos.read_to_end(&mut recibido).unwrap();
    datos.shutdown(std::net::Shutdown::Both).unwrap();
    assert!(cliente.respuesta().starts_with("226 "), "RETR debe completarse");
    assert_eq!(recibido, contenido, "el contenido debe volver idéntico");
}

#[test]
fn stor_respeta_el_limite_de_tamano_y_no_publica_nada() {
    let servidor = ServidorDePrueba::arrancar(&[("FTP_MAX_UPLOAD_BYTES", "100")]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    let puerto_datos = cliente.puerto_pasv();
    cliente.enviar("STOR grande.bin");
    assert!(cliente.respuesta().starts_with("150 "));
    let mut datos = cliente.conectar_datos(puerto_datos);
    datos.write_all(&[0u8; 200]).unwrap();
    datos.shutdown(std::net::Shutdown::Write).unwrap();
    drop(datos);
    let r = cliente.respuesta();
    assert!(r.starts_with("552 "), "debe ser 552 por tamaño: {r}");
    // No se publica nada y no quedan temporales.
    assert!(!servidor.raiz.join("grande.bin").exists());
    assert!(temporales_en(&servidor.raiz).is_empty());
}

#[test]
fn stor_conserva_el_archivo_anterior_si_la_recepcion_falla() {
    // Con 1 s de timeout de datos, la segunda subida se aborta por
    // inactividad con el socket abierto a medias.
    let servidor = ServidorDePrueba::arrancar(&[("FTP_DATA_TIMEOUT", "1")]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();

    // Primera subida completa: publica "hola".
    let puerto_datos = cliente.puerto_pasv();
    cliente.enviar("STOR a.txt");
    assert!(cliente.respuesta().starts_with("150 "));
    let mut datos = cliente.conectar_datos(puerto_datos);
    datos.write_all(b"hola").unwrap();
    datos.shutdown(std::net::Shutdown::Write).unwrap();
    drop(datos);
    assert!(cliente.respuesta().starts_with("226 "));

    // Segunda subida interrumpida: se envían datos parciales y se deja el
    // socket ABIERTO; el servidor debe agotar el timeout y no publicar.
    let puerto_datos = cliente.puerto_pasv();
    cliente.enviar("STOR a.txt");
    assert!(cliente.respuesta().starts_with("150 "));
    let mut datos = cliente.conectar_datos(puerto_datos);
    datos.write_all(b"adios-parciales").unwrap();
    transferencia_abierta_sin_cerrar(&datos);
    let r = cliente.respuesta();
    assert!(
        r.starts_with("426 ") || r.starts_with("450 "),
        "una recepción abortada no puede responder 226: {r}"
    );
    drop(datos);
    assert!(temporales_en(&servidor.raiz).is_empty(), "el temporal debe limpiarse");

    let puerto_datos = cliente.puerto_pasv();
    cliente.enviar("RETR a.txt");
    assert!(cliente.respuesta().starts_with("150 "));
    let mut datos = cliente.conectar_datos(puerto_datos);
    let mut contenido = Vec::new();
    datos.read_to_end(&mut contenido).unwrap();
    datos.shutdown(std::net::Shutdown::Both).unwrap();
    assert!(cliente.respuesta().starts_with("226 "));
    assert_eq!(contenido, b"hola", "el archivo anterior debe quedar intacto");
}

// ---------------------------------------------------------------------------
// Protocolo, límites y tiempo
// ---------------------------------------------------------------------------

#[test]
fn comando_demasiado_largo_responde_500_y_cierra() {
    let servidor = ServidorDePrueba::arrancar(&[("FTP_MAX_COMMAND_BYTES", "64")]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    let largo = "X".repeat(100);
    cliente.enviar_crudo(format!("{largo}\r\n").as_bytes());
    let r = cliente.respuesta();
    assert!(r.starts_with("500 "), "respuesta: {r}");
    assert_eq!(cliente.respuesta_opcional(), None, "la sesión debe cerrarse");
}

#[test]
fn max_clients_rechaza_con_421_sin_bloquear_a_los_demas() {
    let servidor = ServidorDePrueba::arrancar(&[("FTP_MAX_CLIENTS", "1")]);
    // La primera sesión ocupa el único hueco y se queda abierta e inactiva.
    let _ocupada = Cliente::conectar(servidor.puerto);

    let segunda = TcpStream::connect(("127.0.0.1", servidor.puerto)).unwrap();
    configurar_timeouts(&segunda);
    let mut reader = BufReader::new(segunda);
    let mut linea = String::new();
    reader.read_line(&mut linea).unwrap();
    assert!(
        linea.starts_with("421 "),
        "la segunda conexión debe rechazarse con 421: {linea}"
    );
}

#[test]
fn control_timeout_cierra_la_sesion_inactiva() {
    let servidor = ServidorDePrueba::arrancar(&[("FTP_CONTROL_TIMEOUT", "1")]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    thread::sleep(Duration::from_millis(1600));
    assert_eq!(
        cliente.respuesta_opcional(),
        None,
        "el servidor debe cerrar por inactividad del canal de control"
    );
}

#[test]
fn data_connect_timeout_responde_426() {
    let servidor = ServidorDePrueba::arrancar(&[("FTP_DATA_CONNECT_TIMEOUT", "1")]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    let _puerto_datos = cliente.puerto_pasv();
    // Se envía PASV pero NUNCA se conecta el canal de datos.
    cliente.enviar("LIST");
    assert!(cliente.respuesta().starts_with("150 "));
    let r = cliente.respuesta();
    assert!(r.starts_with("426 "), "sin conexión de datos debe ser 426: {r}");
}

#[test]
fn sin_pasv_los_comandos_de_datos_responden_425() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.login();
    cliente.enviar("LIST");
    assert!(cliente.respuesta().starts_with("425 "));
    cliente.enviar("RETR x.txt");
    assert!(cliente.respuesta().starts_with("425 "));
    cliente.enviar("STOR x.txt");
    assert!(cliente.respuesta().starts_with("425 "));
}

#[test]
fn quit_responde_221_y_cierra() {
    let servidor = ServidorDePrueba::arrancar(&[]);
    let mut cliente = Cliente::conectar(servidor.puerto);
    cliente.enviar("QUIT");
    assert!(cliente.respuesta().starts_with("221 "));
    assert_eq!(cliente.respuesta_opcional(), None);
}

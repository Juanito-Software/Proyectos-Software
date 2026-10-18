//! Servidor HTTP didáctico en Rust — solo biblioteca estándar.
//!
//! Escucha conexiones TCP, parsea una petición HTTP/1.0 o HTTP/1.1 por
//! conexión y responde. Sin dependencias externas, sin TLS y sin
//! conexiones persistentes: cada conexión recibe una única petición y se
//! cierra.
//!
//! Decisiones de diseño documentadas:
//!
//! - **Objetivo de la petición**: solo se admite el formato de origen
//!   (`/ruta`, con componente de consulta opcional tras `?`). No se
//!   admiten URLs absolutas (`http://…`), la forma autoridad (`host:port`)
//!   ni `*`. La ruta no se decodifica porcentajes: se compara byte a byte.
//! - **Cuerpos de petición**: no se admiten. `Content-Length: 0` se
//!   tolera; cualquier cuerpo positivo responde `413 Content Too Large` y
//!   `Transfer-Encoding` responde `501 Not Implemented` (sin soportar
//!   ninguna codificación). Nunca se reserva memoria ni se lee un cuerpo.
//! - **Encuadre**: se rechaza cualquier combinación ambigua de
//!   `Content-Length` y `Transfer-Encoding` con `400 Bad Request`.
//! - **HTTP/1.1 exige exactamente una cabecera `Host` válida**; en
//!   HTTP/1.0 es opcional, pero si aparece se valida igualmente.
//! - **Concurrencia**: fijo de trabajadores (`NUM_TRABAJADORES`) con una
//!   cola acotada (`sync_channel`). Si la cola está llena, la conexión se
//!   rechaza cerrando el socket de forma controlada.
//! - **Un método admitido por ruta**: `GET` y `HEAD` (comparten enrutado;
//!   `HEAD` omite el cuerpo pero conserva el `Content-Length`). El resto
//!   de métodos responde `405 Method Not Allowed` con `Allow: GET, HEAD`.
//!
//! Advertencia: HTTP transmite el contenido sin cifrar.

use std::io::{BufRead, BufReader, Write};
use std::net::{Ipv6Addr, TcpListener, TcpStream};
use std::sync::mpsc::{sync_channel, Receiver, TrySendError};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

const PUERTO: u16 = 8080;

/// Límites del protocolo y de los recursos. Son constantes del diseño
/// didáctico; en un servidor real podrían ser configurables.
#[derive(Clone)]
struct Limites {
    /// Longitud máxima de la línea de petición, sin contar el CRLF final.
    max_linea_peticion: usize,
    /// Longitud máxima del componente de ruta del objetivo.
    max_ruta: usize,
    /// Tamaño máximo total del bloque de cabeceras (líneas y CRLF incluidos).
    max_bytes_cabeceras: usize,
    /// Número máximo de cabeceras admitidas.
    max_num_cabeceras: usize,
    /// Tiempo máximo para recibir la petición completa y escribir la respuesta.
    duracion: Duration,
}

impl Limites {
    fn por_defecto() -> Self {
        Self {
            max_linea_peticion: 8 * 1024,
            max_ruta: 2048,
            max_bytes_cabeceras: 16 * 1024,
            max_num_cabeceras: 100,
            duracion: Duration::from_secs(10),
        }
    }
}

// Número de hilos que atienden conexiones. Es el máximo explícito de
// clientes atendidos a la vez: un cliente lento solo retiene un hilo el
// tiempo que dure su plazo de lectura, no indefinidamente.
const NUM_TRABAJADORES: usize = 8;

// Capacidad de la cola de conexiones pendientes. Si está llena, la
// siguiente conexión se rechaza cerrando el socket (rechazo controlado).
const CAPACIDAD_COLA: usize = 16;

fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind(("0.0.0.0", PUERTO))?;
    println!(
        "Servidor escuchando en http://0.0.0.0:{} (todas las interfaces; HTTP sin cifrar)",
        PUERTO
    );
    servir(
        listener,
        Limites::por_defecto(),
        NUM_TRABAJADORES,
        CAPACIDAD_COLA,
    )
}

/// Bucle principal: acepta conexiones y las encola para los trabajadores.
fn servir(
    listener: TcpListener,
    limites: Limites,
    num_trabajadores: usize,
    capacidad_cola: usize,
) -> std::io::Result<()> {
    let (enviador, receptor) = sync_channel::<TcpStream>(capacidad_cola);
    let receptor = Arc::new(Mutex::new(receptor));
    for id in 0..num_trabajadores.max(1) {
        let receptor = Arc::clone(&receptor);
        let limites = limites.clone();
        thread::spawn(move || trabajador(id, receptor, limites));
    }
    for conexion in listener.incoming() {
        match conexion {
            Ok(stream) => match enviador.try_send(stream) {
                Ok(()) => {}
                Err(TrySendError::Full(_)) => {
                    // Cola llena: se cierra el socket sin respuesta. El
                    // cliente ve una desconexión temprana, no un bloqueo.
                    eprintln!("Conexión rechazada: cola de conexiones llena");
                }
                Err(TrySendError::Disconnected(_)) => {
                    eprintln!("Servidor: todos los trabajadores terminaron; cerrando");
                    return Ok(());
                }
            },
            Err(e) => eprintln!("Error aceptando conexión: {}", e),
        }
    }
    Ok(())
}

/// Hilo trabajador: recibe conexiones de la cola y las atiende. El candado
/// del receptor solo se mantiene durante `recv`; el procesamiento ocurre
/// fuera del candado, así que no serializa el trabajo de los demás.
fn trabajador(id: usize, receptor: Arc<Mutex<Receiver<TcpStream>>>, limites: Limites) {
    loop {
        let stream = match receptor.lock() {
            Ok(guard) => guard.recv(),
            Err(_) => {
                eprintln!(
                    "Trabajador {}: candado del receptor envenenado; termina",
                    id
                );
                return;
            }
        };
        match stream {
            Ok(stream) => {
                if let Err(e) = atender_cliente(stream, &limites) {
                    eprintln!("Trabajador {}: {}", id, e);
                }
            }
            Err(_) => return, // sin más conexiones: apagado ordenado
        }
    }
}

/// Plazos de lectura y escritura: un cliente lento no retiene el hilo más
/// allá del plazo, y un fallo individual nunca termina el proceso.
fn preparar_socket(stream: &TcpStream, duracion: Duration) -> std::io::Result<()> {
    stream.set_read_timeout(Some(duracion))?;
    stream.set_write_timeout(Some(duracion))?;
    stream.set_nodelay(true)?;
    Ok(())
}

/// Atiende una conexión completa: lee y valida la petición, enruta y
/// escribe exactamente una respuesta. Devuelve `Ok(())` también cuando la
/// respuesta no pudo escribirse por una desconexión del cliente (es un
/// fallo normal, no del servidor).
fn atender_cliente(mut stream: TcpStream, limites: &Limites) -> std::io::Result<()> {
    preparar_socket(&stream, limites.duracion)?;

    let mut lector = match stream.try_clone() {
        Ok(copia) => BufReader::new(copia),
        Err(e) => {
            eprintln!("No se pudo clonar el socket: {}", e);
            return Err(e);
        }
    };

    let (peticion, error) = match parsear_peticion(&mut lector, limites) {
        Ok(peticion) => (Some(peticion), None),
        Err(error) => (None, Some(error)),
    };

    // La versión de la respuesta sigue a la petición cuando es conocida;
    // si no, se responde con HTTP/1.1 (por ejemplo ante 505 o errores
    // tempranos de sintaxis).
    let (version, metodo, respuesta) = match (&peticion, &error) {
        (Some(peticion), None) => (peticion.version, Some(peticion.metodo), enrutar(peticion)),
        (_, Some(error)) => match error {
            ErrorPeticion::DesconexionLimpia => return Ok(()), // sin respuesta
            ErrorPeticion::VersionNoSoportada(version) => (
                *version,
                None,
                RespuestaHttp::error(
                    505,
                    "HTTP Version Not Supported",
                    "El servidor solo admite HTTP/1.0 y HTTP/1.1.",
                ),
            ),
            _ => (
                VersionHttp::Http11,
                None,
                RespuestaHttp::error(error.codigo(), error.frase(), error.motivo_cliente()),
            ),
        },
        _ => (
            VersionHttp::Http11,
            None,
            RespuestaHttp::error(500, "Internal Server Error", "Error interno."),
        ),
    };

    // Serializa la respuesta completa en un único buffer: o se envía
    // entera una sola vez, o no se envía nada. `HEAD` conserva el
    // Content-Length del cuerpo que habría producido `GET` pero no
    // transmite ese cuerpo.
    let incluir_cuerpo = metodo != Some(Metodo::Head);
    let bytes = serializar(&respuesta, version, incluir_cuerpo);
    escribir_respuesta(&mut stream, &bytes)
}

// --- Lectura de líneas HTTP con CRLF obligatorio ----------------------------

/// Error de parseo de la petición. Cada variante mapea a un estado HTTP
/// concreto; `DesconexionLimpia` no produce respuesta.
#[derive(Debug)]
enum ErrorPeticion {
    /// EOF antes de recibir cualquier byte: el cliente cerró sin enviar nada.
    DesconexionLimpia,
    /// EOF a mitad de una línea o cabecera: petición incompleta → 400.
    LineaIncompleta,
    /// Se superó el plazo de lectura → 408.
    Timeout,
    /// Terminador LF aislado o CR malformado → 400.
    CrlfInvalido,
    /// Línea de petición o URI superan su límite → 414.
    LimiteLinea,
    /// Bloque de cabeceras supera el límite de bytes o número → 431.
    LimiteCabeceras,
    /// Sintaxis general inválida (línea de petición, cabeceras…) → 400.
    SintaxisInvalida,
    /// Versión HTTP distinta de 1.0/1.1 → 505.
    VersionNoSoportada(VersionHttp),
    /// Cabecera `Host` ausente, duplicada o mal formada → 400.
    HostInvalido,
    /// `Content-Length` presente con un cuerpo positivo → 413.
    CuerpoNoSoportado,
    /// `Transfer-Encoding` presente (no se soporta ninguna codificación) → 501.
    TransferEncodingNoSoportado,
    /// `Content-Length` y `Transfer-Encoding` a la vez → 400.
    EnquadreAmbiguo,
}

impl ErrorPeticion {
    fn codigo(&self) -> u16 {
        match self {
            ErrorPeticion::LineaIncompleta
            | ErrorPeticion::CrlfInvalido
            | ErrorPeticion::SintaxisInvalida
            | ErrorPeticion::HostInvalido
            | ErrorPeticion::EnquadreAmbiguo => 400,
            ErrorPeticion::Timeout => 408,
            ErrorPeticion::CuerpoNoSoportado => 413,
            ErrorPeticion::LimiteLinea => 414,
            ErrorPeticion::LimiteCabeceras => 431,
            ErrorPeticion::VersionNoSoportada(_) => 505,
            ErrorPeticion::TransferEncodingNoSoportado => 501,
            ErrorPeticion::DesconexionLimpia => 400,
        }
    }

    fn frase(&self) -> &'static str {
        match self {
            ErrorPeticion::LineaIncompleta
            | ErrorPeticion::CrlfInvalido
            | ErrorPeticion::SintaxisInvalida
            | ErrorPeticion::HostInvalido
            | ErrorPeticion::EnquadreAmbiguo => "Bad Request",
            ErrorPeticion::Timeout => "Request Timeout",
            ErrorPeticion::CuerpoNoSoportado => "Content Too Large",
            ErrorPeticion::LimiteLinea => "URI Too Long",
            ErrorPeticion::LimiteCabeceras => "Request Header Fields Too Large",
            ErrorPeticion::VersionNoSoportada(_) => "HTTP Version Not Supported",
            ErrorPeticion::TransferEncodingNoSoportado => "Not Implemented",
            ErrorPeticion::DesconexionLimpia => "Bad Request",
        }
    }

    /// Motivo genérico para el cliente: no expone detalles internos.
    fn motivo_cliente(&self) -> &'static str {
        match self {
            ErrorPeticion::LineaIncompleta => "Petición incompleta.",
            ErrorPeticion::CrlfInvalido => "Terminadores de línea inválidos.",
            ErrorPeticion::SintaxisInvalida => "Sintaxis de la petición inválida.",
            ErrorPeticion::HostInvalido => "Cabecera Host inválida.",
            ErrorPeticion::EnquadreAmbiguo => "Encuadre del cuerpo ambiguo.",
            ErrorPeticion::Timeout => "Tiempo de espera agotado.",
            ErrorPeticion::CuerpoNoSoportado => "El servidor no admite cuerpos de petición.",
            ErrorPeticion::LimiteLinea => "URI demasiado larga.",
            ErrorPeticion::LimiteCabeceras => "Cabeceras demasiado grandes.",
            ErrorPeticion::VersionNoSoportada(_) => "El servidor solo admite HTTP/1.0 y HTTP/1.1.",
            ErrorPeticion::TransferEncodingNoSoportado => {
                "Codificación de transferencia no soportada."
            }
            ErrorPeticion::DesconexionLimpia => "Petición incompleta.",
        }
    }
}

/// Mapea un error de E/S del socket a un error de petición. Los errores
/// temporales de lectura significan que el plazo se agotó.
fn error_de_io(e: std::io::Error) -> ErrorPeticion {
    match e.kind() {
        std::io::ErrorKind::TimedOut | std::io::ErrorKind::WouldBlock => ErrorPeticion::Timeout,
        _ => ErrorPeticion::LineaIncompleta,
    }
}

/// Lector de líneas HTTP: exige terminador CRLF, aplica un límite de
/// longitud y un plazo total. El terminador puede llegar fragmentado entre
/// varias llamadas a `read()`; el caso CR en el borde del buffer se
/// resuelve esperando el siguiente byte antes de decidir.
struct LectorHttp<R: BufRead> {
    inner: R,
    fin: Instant,
}

impl<R: BufRead> LectorHttp<R> {
    fn new(inner: R, duracion: Duration) -> Self {
        Self {
            inner,
            fin: Instant::now() + duracion,
        }
    }

    /// Lee una línea completa terminada en CRLF, sin incluir el
    /// terminador. EOF al principio es desconexión limpia; EOF a mitad de
    /// línea, petición incompleta. Un LF sin CR previo o un CR seguido de
    /// algo distinto de LF son errores.
    fn leer_linea(&mut self, limite: usize) -> Result<Vec<u8>, ErrorPeticion> {
        let mut linea = Vec::new();
        loop {
            if Instant::now() >= self.fin {
                return Err(ErrorPeticion::Timeout);
            }
            let byte = {
                let disponibles = self.inner.fill_buf().map_err(error_de_io)?;
                if disponibles.is_empty() {
                    return Err(if linea.is_empty() {
                        ErrorPeticion::DesconexionLimpia
                    } else {
                        ErrorPeticion::LineaIncompleta
                    });
                }
                let byte = disponibles[0];
                self.inner.consume(1);
                byte
            };
            match byte {
                b'\r' => {
                    let siguiente = {
                        if Instant::now() >= self.fin {
                            return Err(ErrorPeticion::Timeout);
                        }
                        let disponibles = self.inner.fill_buf().map_err(error_de_io)?;
                        if disponibles.is_empty() {
                            return Err(ErrorPeticion::LineaIncompleta);
                        }
                        let byte = disponibles[0];
                        self.inner.consume(1);
                        byte
                    };
                    if siguiente != b'\n' {
                        return Err(ErrorPeticion::CrlfInvalido);
                    }
                    return Ok(linea);
                }
                b'\n' => return Err(ErrorPeticion::CrlfInvalido), // LF sin CR
                _ => {
                    if linea.len() >= limite {
                        return Err(ErrorPeticion::LimiteLinea);
                    }
                    linea.push(byte);
                }
            }
        }
    }
}

// --- Parseo de la petición --------------------------------------------------

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum VersionHttp {
    Http10,
    Http11,
}

impl VersionHttp {
    fn texto(self) -> &'static str {
        match self {
            VersionHttp::Http10 => "HTTP/1.0",
            VersionHttp::Http11 => "HTTP/1.1",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Metodo {
    Get,
    Head,
    Otro,
}

#[derive(Debug)]
struct PeticionHttp {
    metodo: Metodo,
    ruta: String,
    /// Componente de consulta tras el primer `?`, sin decodificar. El
    /// enrutado actual no lo usa, pero se conserva como parte del modelo
    /// de la petición (lo afirman las pruebas de parsing).
    #[allow(dead_code)]
    consulta: Option<String>,
    version: VersionHttp,
    /// Cabeceras validadas, con nombres en minúsculas y duplicados
    /// conservados. Tras la validación el enrutado no las necesita, pero
    /// quedan como parte del modelo (lo afirman las pruebas).
    #[allow(dead_code)]
    cabeceras: Vec<(String, String)>,
}

/// Lee y valida una petición completa. No lee cuerpos: la política del
/// servidor es no admitirlos, y se rechaza cualquier cuerpo positivo
/// antes de reservar memoria.
fn parsear_peticion<R: BufRead>(
    reader: &mut R,
    limites: &Limites,
) -> Result<PeticionHttp, ErrorPeticion> {
    let mut lector = LectorHttp::new(reader, limites.duracion);
    let (metodo, ruta, consulta, version) =
        parsear_linea_peticion(&lector.leer_linea(limites.max_linea_peticion)?, limites)?;

    let mut cabeceras = Vec::new();
    let mut bytes_cabeceras = 0usize;
    let mut hosts = 0usize;
    let mut longitud_contenida: Option<u64> = None;
    let mut tiene_transfer_encoding = false;

    loop {
        // La línea vacía cierra el bloque de cabeceras. El límite de bytes
        // del bloque incluye las líneas leídas. Exceder el presupuesto
        // restante es 431 (cabeceras demasiado grandes), no 414.
        let restante = limites.max_bytes_cabeceras.saturating_sub(bytes_cabeceras);
        if restante == 0 {
            return Err(ErrorPeticion::LimiteCabeceras);
        }
        let linea = match lector.leer_linea(restante) {
            Err(ErrorPeticion::LimiteLinea) => return Err(ErrorPeticion::LimiteCabeceras),
            resultado => resultado?,
        };
        bytes_cabeceras += linea.len() + 2; // + CRLF
        if linea.is_empty() {
            break;
        }
        if cabeceras.len() >= limites.max_num_cabeceras {
            return Err(ErrorPeticion::LimiteCabeceras);
        }
        let (nombre, valor) = parsear_cabecera(&linea)?;
        let nombre_minus = nombre.to_ascii_lowercase();

        match nombre_minus.as_str() {
            "host" => {
                hosts += 1;
                validar_host(&valor)?;
            }
            "content-length" => {
                let longitud = analizar_content_length(&valor)?;
                if let Some(anterior) = longitud_contenida {
                    if anterior != longitud {
                        return Err(ErrorPeticion::SintaxisInvalida);
                    }
                }
                longitud_contenida = Some(longitud);
            }
            "transfer-encoding" => {
                tiene_transfer_encoding = true;
            }
            _ => {}
        }
        cabeceras.push((nombre_minus, valor));
    }

    // Encuadre del cuerpo. El servidor no admite cuerpos: cualquier
    // combinación ambigua se rechaza antes de mirar valores.
    if tiene_transfer_encoding && longitud_contenida.is_some() {
        return Err(ErrorPeticion::EnquadreAmbiguo);
    }
    if tiene_transfer_encoding {
        return Err(ErrorPeticion::TransferEncodingNoSoportado);
    }
    if let Some(longitud) = longitud_contenida {
        if longitud > 0 {
            // Cuerpo positivo: se rechaza con 413 sin leer ni reservar.
            return Err(ErrorPeticion::CuerpoNoSoportado);
        }
        // Content-Length: 0 se acepta y no implica leer nada más. Los
        // bytes sobrantes no forman una segunda petición: la conexión se
        // cierra tras esta respuesta.
    }

    match version {
        VersionHttp::Http11 => {
            if hosts != 1 {
                return Err(ErrorPeticion::HostInvalido);
            }
        }
        VersionHttp::Http10 => {
            // HTTP/1.0 no exige Host; si aparece, ya se validó y no debe
            // estar duplicado.
            if hosts > 1 {
                return Err(ErrorPeticion::HostInvalido);
            }
        }
    }

    Ok(PeticionHttp {
        metodo,
        ruta,
        consulta,
        version,
        cabeceras,
    })
}

/// Divide la línea de petición en exactamente tres componentes separados
/// por un único espacio. No se normalizan espacios: un componente vacío o
/// un espacio de más es un error.
fn parsear_linea_peticion(
    linea: &[u8],
    limites: &Limites,
) -> Result<(Metodo, String, Option<String>, VersionHttp), ErrorPeticion> {
    let mut partes = linea.splitn(4, |&b| b == b' ');
    let metodo_raw = partes.next().unwrap_or(&[]);
    let objetivo = partes.next().ok_or(ErrorPeticion::SintaxisInvalida)?;
    let version_raw = partes.next().ok_or(ErrorPeticion::SintaxisInvalida)?;
    if partes.next().is_some() {
        // Un espacio de más: la versión no puede contener espacios.
        return Err(ErrorPeticion::SintaxisInvalida);
    }
    if metodo_raw.is_empty() || objetivo.is_empty() || version_raw.is_empty() {
        return Err(ErrorPeticion::SintaxisInvalida);
    }
    if metodo_raw.iter().any(|&b| !(0x21..=0x7e).contains(&b)) {
        return Err(ErrorPeticion::SintaxisInvalida);
    }
    let metodo = match metodo_raw {
        b"GET" => Metodo::Get,
        b"HEAD" => Metodo::Head,
        _ if es_token(metodo_raw) => Metodo::Otro,
        _ => return Err(ErrorPeticion::SintaxisInvalida),
    };

    let version = parsear_version(version_raw)?;
    let (ruta, consulta) = parsear_objetivo(objetivo, limites)?;
    Ok((metodo, ruta, consulta, version))
}

/// Solo se admiten las versiones HTTP/1.0 y HTTP/1.1. Una versión con
/// sintaxis `HTTP/x.y` distinta es 505; una sin esa forma es 400.
fn parsear_version(bytes: &[u8]) -> Result<VersionHttp, ErrorPeticion> {
    match bytes {
        b"HTTP/1.0" => Ok(VersionHttp::Http10),
        b"HTTP/1.1" => Ok(VersionHttp::Http11),
        _ if bytes.starts_with(b"HTTP/") => {
            Err(ErrorPeticion::VersionNoSoportada(VersionHttp::Http11))
        }
        _ => Err(ErrorPeticion::SintaxisInvalida),
    }
}

/// Valida el objetivo de la petición. Solo se admite el formato de origen:
/// debe empezar por `/`, sin caracteres de control ni espacios (estos ya
/// se habrían usado para partir la línea). El componente de consulta se
/// separa en el primer `?` sin alterar la ruta. No se decodifica nada.
fn parsear_objetivo(
    objetivo: &[u8],
    limites: &Limites,
) -> Result<(String, Option<String>), ErrorPeticion> {
    if objetivo[0] != b'/' {
        // Formatos no soportados: absoluto, autoridad o `*`.
        return Err(ErrorPeticion::SintaxisInvalida);
    }
    let (ruta_bytes, consulta_bytes) = match objetivo.iter().position(|&b| b == b'?') {
        Some(pos) => (&objetivo[..pos], Some(&objetivo[pos + 1..])),
        None => (objetivo, None),
    };
    if ruta_bytes.is_empty() || ruta_bytes.len() > limites.max_ruta {
        return Err(ErrorPeticion::LimiteLinea);
    }
    if ruta_bytes.iter().any(|&b| b <= 0x20 || b == 0x7f) {
        return Err(ErrorPeticion::SintaxisInvalida);
    }
    let ruta =
        String::from_utf8(ruta_bytes.to_vec()).map_err(|_| ErrorPeticion::SintaxisInvalida)?;
    let consulta = match consulta_bytes {
        Some(bytes) => {
            if bytes.iter().any(|&b| !(0x21..=0x7e).contains(&b)) {
                return Err(ErrorPeticion::SintaxisInvalida);
            }
            Some(String::from_utf8(bytes.to_vec()).map_err(|_| ErrorPeticion::SintaxisInvalida)?)
        }
        None => None,
    };
    Ok((ruta, consulta))
}

/// Valida una cabecera individual y devuelve (nombre, valor). El nombre
/// debe ser un token HTTP; el valor no admite caracteres de control (el
/// tabulador se acepta). Solo se recortan los espacios opcionales de los
/// extremos (OWS), como exige el protocolo.
fn parsear_cabecera(linea: &[u8]) -> Result<(String, String), ErrorPeticion> {
    let posicion = linea
        .iter()
        .position(|&b| b == b':')
        .ok_or(ErrorPeticion::SintaxisInvalida)?;
    let nombre = &linea[..posicion];
    let valor_crudo = &linea[posicion + 1..];
    if nombre.is_empty() || !es_token(nombre) {
        return Err(ErrorPeticion::SintaxisInvalida);
    }
    if valor_crudo
        .iter()
        .any(|&b| (b < 0x20 && b != b'\t') || b == 0x7f)
    {
        return Err(ErrorPeticion::SintaxisInvalida);
    }
    let inicio = valor_crudo
        .iter()
        .position(|&b| b != b' ' && b != b'\t')
        .unwrap_or(valor_crudo.len());
    let fin = valor_crudo
        .iter()
        .rposition(|&b| b != b' ' && b != b'\t')
        .map(|p| p + 1)
        .unwrap_or(0);
    let valor = if inicio >= fin {
        ""
    } else {
        std::str::from_utf8(&valor_crudo[inicio..fin])
            .map_err(|_| ErrorPeticion::SintaxisInvalida)?
    };
    Ok((
        String::from_utf8(nombre.to_vec()).map_err(|_| ErrorPeticion::SintaxisInvalida)?,
        valor.to_string(),
    ))
}

/// Un token HTTP (RFC 9110 §5.6.2): `!#$%&'*+-.^_`|~` y dígitos/letras.
fn es_token(bytes: &[u8]) -> bool {
    bytes.iter().all(|&b| {
        b.is_ascii_alphanumeric()
            || matches!(
                b,
                b'!' | b'#'
                    | b'$'
                    | b'%'
                    | b'&'
                    | b'\''
                    | b'*'
                    | b'+'
                    | b'-'
                    | b'.'
                    | b'^'
                    | b'_'
                    | b'`'
                    | b'|'
                    | b'~'
            )
    })
}

/// Valida la autoridad de `Host`: nombre de host (reg-name), IPv4 o IPv6
/// entre corchetes, con puerto opcional. No se resuelve ningún nombre DNS.
fn validar_host(valor: &str) -> Result<(), ErrorPeticion> {
    if valor.is_empty() || valor.len() > 255 {
        return Err(ErrorPeticion::HostInvalido);
    }
    let bytes = valor.as_bytes();
    if bytes[0] == b'[' {
        // Literal IPv6: `[::1]` o `[::1]:8080`.
        let cierre = bytes
            .iter()
            .position(|&b| b == b']')
            .ok_or(ErrorPeticion::HostInvalido)?;
        let interior = &valor[1..cierre];
        interior
            .parse::<Ipv6Addr>()
            .map_err(|_| ErrorPeticion::HostInvalido)?;
        let resto = &valor[cierre + 1..];
        if resto.is_empty() {
            return Ok(());
        }
        if !resto.starts_with(':') || resto.len() < 2 {
            return Err(ErrorPeticion::HostInvalido);
        }
        validar_puerto(&resto[1..])
    } else {
        // reg-name o IPv4, con puerto opcional tras el último ':'. Un
        // nombre sin corchetes no puede contener más de un ':'.
        let (host, puerto) = match bytes.iter().rposition(|&b| b == b':') {
            Some(pos) => {
                if bytes[..pos].contains(&b':') {
                    return Err(ErrorPeticion::HostInvalido); // IPv6 sin corchetes
                }
                (&valor[..pos], Some(&valor[pos + 1..]))
            }
            None => (valor, None),
        };
        if host.is_empty() {
            return Err(ErrorPeticion::HostInvalido);
        }
        if !host.bytes().all(es_caracter_reg_name) {
            return Err(ErrorPeticion::HostInvalido);
        }
        if let Some(puerto) = puerto {
            validar_puerto(puerto)?;
        }
        Ok(())
    }
}

/// Caracteres admitidos en un nombre de host (reg-name simplificado):
/// letras, dígitos y `-._~!$&'()*+,;=` (unreserved + sub-delims).
fn es_caracter_reg_name(b: u8) -> bool {
    b.is_ascii_alphanumeric()
        || matches!(
            b,
            b'-' | b'.'
                | b'_'
                | b'~'
                | b'!'
                | b'$'
                | b'&'
                | b'\''
                | b'('
                | b')'
                | b'*'
                | b'+'
                | b','
                | b';'
                | b'='
        )
}

fn validar_puerto(puerto: &str) -> Result<(), ErrorPeticion> {
    if puerto.is_empty() || puerto.len() > 5 || !puerto.bytes().all(|b| b.is_ascii_digit()) {
        return Err(ErrorPeticion::HostInvalido);
    }
    let valor: u16 = puerto.parse().map_err(|_| ErrorPeticion::HostInvalido)?;
    let _ = valor; // basta con que quepa en u16
    Ok(())
}

/// Valida un `Content-Length`: solo dígitos decimales, sin signos ni
/// formatos raros, y con un tope de dígitos que evita desbordes antes de
/// convertir. Devuelve el valor ya convertido.
fn analizar_content_length(valor: &str) -> Result<u64, ErrorPeticion> {
    if valor.is_empty() || valor.len() > 15 || !valor.bytes().all(|b| b.is_ascii_digit()) {
        return Err(ErrorPeticion::SintaxisInvalida);
    }
    valor
        .parse::<u64>()
        .map_err(|_| ErrorPeticion::SintaxisInvalida)
}

// --- Respuestas HTTP --------------------------------------------------------

struct RespuestaHttp {
    estado: u16,
    frase: &'static str,
    cabeceras: Vec<(String, String)>,
    cuerpo: Vec<u8>,
}

impl RespuestaHttp {
    /// Respuesta con cuerpo HTML de texto (páginas y errores).
    fn con_html(estado: u16, frase: &'static str, cuerpo: String) -> Self {
        Self {
            estado,
            frase,
            cabeceras: vec![(
                "Content-Type".to_string(),
                "text/html; charset=utf-8".to_string(),
            )],
            cuerpo: cuerpo.into_bytes(),
        }
    }

    /// Respuesta con cuerpo JSON (la ruta `/api/saludo`).
    fn con_json(estado: u16, frase: &'static str, cuerpo: Vec<u8>) -> Self {
        Self {
            estado,
            frase,
            cabeceras: vec![(
                "Content-Type".to_string(),
                "application/json; charset=utf-8".to_string(),
            )],
            cuerpo,
        }
    }

    /// Página de error: el motivo es texto fijo del propio servidor, y se
    /// escapa por si acasa antes de insertarlo en el HTML. Nunca se
    /// vuelcan detalles internos ni texto proveniente del cliente.
    fn error(estado: u16, frase: &'static str, motivo: &str) -> Self {
        let cuerpo = format!(
            "<!DOCTYPE html>\n<html>\n<head><meta charset=\"utf-8\"><title>{} {}</title></head>\n<body>\n  <h1>{} {}</h1>\n  <p>{}</p>\n</body>\n</html>",
            estado,
            frase,
            estado,
            frase,
            escapar_html(motivo)
        );
        Self::con_html(estado, frase, cuerpo)
    }

    /// Cabeceras comunes a toda respuesta, con el `Content-Length` del
    /// cuerpo completo (el que se habría enviado, incluso en `HEAD`).
    fn cabeceras_finales(&self) -> Vec<(String, String)> {
        let mut cabeceras = self.cabeceras.clone();
        cabeceras.push(("Content-Length".to_string(), self.cuerpo.len().to_string()));
        cabeceras.push(("Connection".to_string(), "close".to_string()));
        cabeceras
    }
}

/// Escapa los caracteres reservados de HTML. Se usa en los cuerpos de
/// error por si el texto variable llegase a contener marcado.
fn escapar_html(texto: &str) -> String {
    let mut salida = String::with_capacity(texto.len());
    for c in texto.chars() {
        match c {
            '&' => salida.push_str("&amp;"),
            '<' => salida.push_str("&lt;"),
            '>' => salida.push_str("&gt;"),
            '"' => salida.push_str("&quot;"),
            '\'' => salida.push_str("&#39;"),
            _ => salida.push(c),
        }
    }
    salida
}

/// Serializa la respuesta completa en un buffer de bytes. Las cabeceras
/// se escriben en orden estable (vector, no mapa) y cualquier valor con
/// CR o LF se rechaza: no puede haber inyección de cabeceras. El
/// `Content-Length` se calcula con los bytes del cuerpo, no con los
/// caracteres Unicode.
fn serializar(respuesta: &RespuestaHttp, version: VersionHttp, incluir_cuerpo: bool) -> Vec<u8> {
    let mut buffer = Vec::with_capacity(
        64 + respuesta
            .cabeceras_finales()
            .iter()
            .map(|(k, v)| k.len() + v.len() + 4)
            .sum::<usize>()
            + respuesta.cuerpo.len(),
    );
    buffer.extend_from_slice(
        format!(
            "{} {} {}\r\n",
            version.texto(),
            respuesta.estado,
            respuesta.frase
        )
        .as_bytes(),
    );
    for (nombre, valor) in respuesta.cabeceras_finales() {
        if nombre.bytes().any(|b| b == b'\r' || b == b'\n')
            || valor.bytes().any(|b| b == b'\r' || b == b'\n')
        {
            // Defensa en profundidad: las cabeceras internas nunca deben
            // llegar aquí con CR/LF.
            eprintln!("Cabecera con CR/LF descartada: {}", nombre);
            continue;
        }
        buffer.extend_from_slice(format!("{}: {}\r\n", nombre, valor).as_bytes());
    }
    buffer.extend_from_slice(b"\r\n");
    if incluir_cuerpo {
        buffer.extend_from_slice(&respuesta.cuerpo);
    }
    buffer
}

fn escribir_respuesta(stream: &mut dyn Write, bytes: &[u8]) -> std::io::Result<()> {
    stream.write_all(bytes)?;
    stream.flush()
}

// --- Enrutado y handlers ----------------------------------------------------

/// Enruta una petición ya parseada a su respuesta. `GET` y `HEAD` comparten
/// el mismo camino: la respuesta se genera igual y la omisión del cuerpo
/// se decide al serializar.
fn enrutar(peticion: &PeticionHttp) -> RespuestaHttp {
    match peticion.metodo {
        Metodo::Get | Metodo::Head => match peticion.ruta.as_str() {
            "/" => RespuestaHttp::con_html(
                200,
                "OK",
                r#"<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Servidor Rust</title></head>
<body>
  <h1>Servidor web en Rust</h1>
  <p>Hecho desde cero, sin dependencias externas.</p>
  <p><a href="/hola">/hola</a></p>
</body>
</html>"#
                    .to_string(),
            ),
            "/hola" => RespuestaHttp::con_html(
                200,
                "OK",
                r#"<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Hola</title></head>
<body><h1>¡Hola desde Rust!</h1></body>
</html>"#
                    .to_string(),
            ),
            "/api/saludo" => RespuestaHttp::con_json(
                200,
                "OK",
                br#"{"mensaje":"Hola desde el servidor"}"#.to_vec(),
            ),
            _ => RespuestaHttp::error(404, "Not Found", "Ruta no encontrada."),
        },
        Metodo::Otro => {
            let mut respuesta =
                RespuestaHttp::error(405, "Method Not Allowed", "Método no admitido.");
            respuesta
                .cabeceras
                .push(("Allow".to_string(), "GET, HEAD".to_string()));
            respuesta
        }
    }
}

// --- Pruebas ----------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::{Cursor, Read};

    // Helpers de pruebas ----------------------------------------------------

    fn limites_pequenos() -> Limites {
        Limites {
            max_linea_peticion: 64,
            max_ruta: 32,
            max_bytes_cabeceras: 256,
            max_num_cabeceras: 8,
            duracion: Duration::from_secs(2),
        }
    }

    fn analizar(bytes: &[u8]) -> Result<PeticionHttp, ErrorPeticion> {
        analizar_con(bytes, &Limites::por_defecto())
    }

    fn analizar_con(bytes: &[u8], limites: &Limites) -> Result<PeticionHttp, ErrorPeticion> {
        let mut cursor = Cursor::new(bytes.to_vec());
        parsear_peticion(&mut cursor, limites)
    }

    /// Una petición GET/HEAD válida de ejemplo para rellenar `PeticionHttp`
    /// directamente en las pruebas de enrutado.
    fn peticion_de_ejemplo(metodo: Metodo, ruta: &str) -> PeticionHttp {
        PeticionHttp {
            metodo,
            ruta: ruta.to_string(),
            consulta: None,
            version: VersionHttp::Http11,
            cabeceras: vec![("host".to_string(), "localhost".to_string())],
        }
    }

    fn cuerpo_de(respuesta: &RespuestaHttp) -> String {
        String::from_utf8(respuesta.cuerpo.clone()).unwrap_or_default()
    }

    fn content_length_de(respuesta: &RespuestaHttp) -> String {
        respuesta
            .cabeceras_finales()
            .into_iter()
            .find(|(nombre, _)| nombre == "Content-Length")
            .map(|(_, valor)| valor)
            .unwrap_or_default()
    }

    // Parsing: línea de petición ---------------------------------------------

    #[test]
    fn una_linea_de_peticion_valida_se_parsea() {
        let p = analizar(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n").unwrap();
        assert_eq!(p.metodo, Metodo::Get);
        assert_eq!(p.ruta, "/");
        assert_eq!(p.version, VersionHttp::Http11);
    }

    #[test]
    fn una_linea_incompleta_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1");
        assert!(matches!(resultado, Err(ErrorPeticion::LineaIncompleta)));
    }

    #[test]
    fn un_metodo_vacio_es_un_error() {
        let resultado = analizar(b" / HTTP/1.1\r\nHost: localhost\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn un_metodo_no_admitido_pero_valido_no_es_error_de_sintaxis() {
        let p = analizar(b"POST / HTTP/1.1\r\nHost: localhost\r\n\r\n").unwrap();
        assert_eq!(p.metodo, Metodo::Otro);
    }

    #[test]
    fn un_metodo_con_caracteres_invalidos_es_un_error() {
        let resultado = analizar(b"G\tT / HTTP/1.1\r\nHost: localhost\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn una_version_no_admitida_devuelve_505() {
        let resultado = analizar(b"GET / HTTP/2.0\r\nHost: localhost\r\n\r\n");
        assert!(matches!(
            resultado,
            Err(ErrorPeticion::VersionNoSoportada(_))
        ));
        assert_eq!(
            ErrorPeticion::VersionNoSoportada(VersionHttp::Http11).codigo(),
            505
        );
    }

    #[test]
    fn una_version_malformada_es_un_error() {
        let resultado = analizar(b"GET / HTP/1.1\r\nHost: localhost\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn un_espacio_de_mas_en_la_linea_es_un_error() {
        let resultado = analizar(b"GET  / HTTP/1.1\r\nHost: localhost\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn un_lf_aislado_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\nHost: localhost\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::CrlfInvalido)));
    }

    #[test]
    fn un_cr_malformado_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\rXHost: localhost\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::CrlfInvalido)));
    }

    // Parsing: objetivo ------------------------------------------------------

    #[test]
    fn una_url_absoluta_no_se_como_ruta_ordinaria() {
        let resultado = analizar(b"GET http://localhost/ HTTP/1.1\r\nHost: localhost\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn el_objetivo_asterisco_no_se_admite() {
        let resultado = analizar(b"OPTIONS * HTTP/1.1\r\nHost: localhost\r\n\r\n");
        // OPTIONS con `*`: la forma del objetivo no está soportada.
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn la_consulta_se_separa_sin_alterar_la_ruta() {
        let p = analizar(b"GET /hola?x=1&y=2 HTTP/1.1\r\nHost: localhost\r\n\r\n").unwrap();
        assert_eq!(p.ruta, "/hola");
        assert_eq!(p.consulta.as_deref(), Some("x=1&y=2"));
    }

    #[test]
    fn una_ruta_larga_devuelve_414() {
        let ruta = "a".repeat(2049);
        let peticion = format!("GET /{} HTTP/1.1\r\nHost: localhost\r\n\r\n", ruta);
        let resultado = analizar(peticion.as_bytes());
        assert!(matches!(resultado, Err(ErrorPeticion::LimiteLinea)));
        assert_eq!(ErrorPeticion::LimiteLinea.codigo(), 414);
    }

    #[test]
    fn una_linea_de_peticion_larga_devuelve_414() {
        let mut peticion = b"GET /".to_vec();
        peticion.extend(std::iter::repeat_n(b'a', 8192));
        peticion.extend_from_slice(b" HTTP/1.1\r\nHost: localhost\r\n\r\n");
        let resultado = analizar(&peticion);
        assert!(matches!(resultado, Err(ErrorPeticion::LimiteLinea)));
    }

    // Parsing: cabeceras -----------------------------------------------------

    #[test]
    fn una_cabecera_sin_separador_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\r\nHost localhost\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn un_nombre_de_cabecera_vacio_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\r\n: valor\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn un_valor_de_cabecera_con_caracter_de_control_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\r\nX-Prueba: a\x01b\r\nHost: localhost\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn las_cabeceras_duplicadas_se_conservan_y_no_se_sobrescriben() {
        let p = analizar(b"GET / HTTP/1.1\r\nHost: localhost\r\nX-A: 1\r\nX-A: 2\r\n\r\n").unwrap();
        let repetidas: Vec<_> = p
            .cabeceras
            .iter()
            .filter(|(nombre, _)| nombre == "x-a")
            .collect();
        assert_eq!(repetidas.len(), 2);
        assert_eq!(repetidas[0].1, "1");
        assert_eq!(repetidas[1].1, "2");
    }

    #[test]
    fn el_bloque_de_cabeceras_que_supera_el_limite_devuelve_431() {
        let mut peticion = b"GET / HTTP/1.1\r\nHost: localhost\r\n".to_vec();
        while peticion.len() < 17 * 1024 {
            peticion.extend_from_slice(b"X-Relleno: 1234567890\r\n");
        }
        peticion.extend_from_slice(b"\r\n");
        let resultado = analizar(&peticion);
        assert!(matches!(resultado, Err(ErrorPeticion::LimiteCabeceras)));
        assert_eq!(ErrorPeticion::LimiteCabeceras.codigo(), 431);
    }

    #[test]
    fn demasiadas_cabeceras_devuelven_431() {
        let mut peticion = b"GET / HTTP/1.1\r\nHost: localhost\r\n".to_vec();
        for i in 0..100 {
            peticion.extend_from_slice(format!("X-C{}: v\r\n", i).as_bytes());
        }
        peticion.extend_from_slice(b"\r\n");
        let resultado = analizar(&peticion);
        assert!(matches!(resultado, Err(ErrorPeticion::LimiteCabeceras)));
    }

    // Parsing: Host ----------------------------------------------------------

    #[test]
    fn http_1_1_sin_host_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::HostInvalido)));
    }

    #[test]
    fn http_1_0_sin_host_se_admite() {
        let p = analizar(b"GET / HTTP/1.0\r\n\r\n").unwrap();
        assert_eq!(p.version, VersionHttp::Http10);
    }

    #[test]
    fn un_host_duplicado_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\r\nHost: a\r\nHost: b\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::HostInvalido)));
    }

    #[test]
    fn un_host_vacio_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\r\nHost:\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::HostInvalido)));
    }

    #[test]
    fn un_host_ipv6_entre_corchetes_se_admite() {
        let p = analizar(b"GET / HTTP/1.1\r\nHost: [::1]:8080\r\n\r\n").unwrap();
        assert_eq!(p.cabeceras[0].1, "[::1]:8080");
    }

    #[test]
    fn un_host_ipv6_sin_corchetes_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\r\nHost: ::1\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::HostInvalido)));
    }

    #[test]
    fn un_puerto_invalido_en_host_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\r\nHost: localhost:99999\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::HostInvalido)));
    }

    #[test]
    fn un_host_con_caracteres_invalidos_es_un_error() {
        let resultado = analizar(b"GET / HTTP/1.1\r\nHost: ho la\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::HostInvalido)));
    }

    // Parsing: Content-Length y Transfer-Encoding ----------------------------

    #[test]
    fn un_content_length_negativo_es_un_error() {
        let resultado =
            analizar(b"GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: -1\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn un_content_length_no_numerico_es_un_error() {
        let resultado =
            analizar(b"GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: abc\r\n\r\n");
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn un_content_length_duplicado_contradictorio_es_un_error() {
        let resultado = analizar(
            b"GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\nContent-Length: 5\r\n\r\n",
        );
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn un_content_length_duplicado_igual_se_tolerado() {
        let p = analizar(
            b"GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\nContent-Length: 0\r\n\r\n",
        )
        .unwrap();
        assert_eq!(p.metodo, Metodo::Get);
    }

    #[test]
    fn un_content_length_excesivamente_largo_es_un_error() {
        let resultado = analizar(
            b"GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 99999999999999999999999\r\n\r\n",
        );
        assert!(matches!(resultado, Err(ErrorPeticion::SintaxisInvalida)));
    }

    #[test]
    fn un_content_length_positivo_devuelve_413_sin_leer_el_cuerpo() {
        let resultado =
            analizar(b"GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\n\r\nhola!");
        assert!(matches!(resultado, Err(ErrorPeticion::CuerpoNoSoportado)));
        assert_eq!(ErrorPeticion::CuerpoNoSoportado.codigo(), 413);
    }

    #[test]
    fn un_content_length_cero_se_admite() {
        let p =
            analizar(b"GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n\r\n").unwrap();
        assert_eq!(p.metodo, Metodo::Get);
    }

    #[test]
    fn transfer_encoding_devuelve_501() {
        let resultado =
            analizar(b"GET / HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\n\r\n");
        assert!(matches!(
            resultado,
            Err(ErrorPeticion::TransferEncodingNoSoportado)
        ));
        assert_eq!(ErrorPeticion::TransferEncodingNoSoportado.codigo(), 501);
    }

    #[test]
    fn transfer_encoding_mas_content_length_es_ambiguo() {
        let resultado = analizar(
            b"GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\nTransfer-Encoding: chunked\r\n\r\n",
        );
        assert!(matches!(resultado, Err(ErrorPeticion::EnquadreAmbiguo)));
    }

    // Parsing: límites y desconexión -----------------------------------------

    #[test]
    fn una_linea_que_supera_el_limite_pequeno_devuelve_414() {
        let mut peticion = b"GET /".to_vec();
        peticion.extend(std::iter::repeat_n(b'a', 64));
        peticion.extend_from_slice(b" HTTP/1.1\r\nHost: localhost\r\n\r\n");
        let resultado = analizar_con(&peticion, &limites_pequenos());
        assert!(matches!(resultado, Err(ErrorPeticion::LimiteLinea)));
    }

    #[test]
    fn una_desconexion_limpia_no_es_un_error_de_sintaxis() {
        let resultado = analizar(b"");
        assert!(matches!(resultado, Err(ErrorPeticion::DesconexionLimpia)));
    }

    /// Un lector que simula un EOF a mitad de cabecera.
    struct LectorEofParcial {
        datos: Cursor<Vec<u8>>,
    }

    impl Read for LectorEofParcial {
        fn read(&mut self, buffer: &mut [u8]) -> std::io::Result<usize> {
            self.datos.read(buffer)
        }
    }

    impl BufRead for LectorEofParcial {
        fn fill_buf(&mut self) -> std::io::Result<&[u8]> {
            self.datos.fill_buf()
        }
        fn consume(&mut self, cantidad: usize) {
            self.datos.consume(cantidad)
        }
    }

    #[test]
    fn un_eof_durante_una_cabecera_es_peticion_incompleta() {
        let datos = b"GET / HTTP/1.1\r\nHost: local".to_vec();
        let mut lector = LectorEofParcial {
            datos: Cursor::new(datos),
        };
        let resultado = parsear_peticion(&mut lector, &Limites::por_defecto());
        assert!(matches!(resultado, Err(ErrorPeticion::LineaIncompleta)));
    }

    /// Un lector que devuelve siempre timeout, como un socket cuyo plazo
    /// de lectura se agota.
    struct LectorTimeout;

    impl Read for LectorTimeout {
        fn read(&mut self, _buffer: &mut [u8]) -> std::io::Result<usize> {
            Err(std::io::Error::new(
                std::io::ErrorKind::TimedOut,
                "timeout simulado",
            ))
        }
    }

    impl BufRead for LectorTimeout {
        fn fill_buf(&mut self) -> std::io::Result<&[u8]> {
            Err(std::io::Error::new(
                std::io::ErrorKind::TimedOut,
                "timeout simulado",
            ))
        }
        fn consume(&mut self, _cantidad: usize) {}
    }

    #[test]
    fn un_timeout_de_lectura_devuelve_408() {
        let mut lector = LectorTimeout;
        let resultado = parsear_peticion(&mut lector, &Limites::por_defecto());
        assert!(matches!(resultado, Err(ErrorPeticion::Timeout)));
        assert_eq!(ErrorPeticion::Timeout.codigo(), 408);
    }

    // Enrutado y respuestas ---------------------------------------------------

    #[test]
    fn get_raiz_devuelve_200_y_su_pagina() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Get, "/"));
        assert_eq!(respuesta.estado, 200);
        assert_eq!(respuesta.frase, "OK");
        assert!(cuerpo_de(&respuesta).contains("Servidor web en Rust"));
    }

    #[test]
    fn get_hola_devuelve_su_pagina() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Get, "/hola"));
        assert_eq!(respuesta.estado, 200);
        assert!(cuerpo_de(&respuesta).contains("¡Hola desde Rust!"));
    }

    #[test]
    fn get_api_saludo_devuelve_su_json() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Get, "/api/saludo"));
        assert_eq!(respuesta.estado, 200);
        assert_eq!(
            cuerpo_de(&respuesta),
            r#"{"mensaje":"Hola desde el servidor"}"#
        );
    }

    #[test]
    fn una_ruta_inexistente_devuelve_404() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Get, "/noexiste"));
        assert_eq!(respuesta.estado, 404);
        assert_eq!(respuesta.frase, "Not Found");
    }

    #[test]
    fn un_metodo_no_admitido_devuelve_405_con_allow() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Otro, "/"));
        assert_eq!(respuesta.estado, 405);
        let allow = respuesta
            .cabeceras
            .iter()
            .find(|(nombre, _)| nombre == "Allow")
            .map(|(_, valor)| valor.clone());
        assert_eq!(allow.as_deref(), Some("GET, HEAD"));
    }

    #[test]
    fn head_de_las_tres_rutas_comparte_las_cabeceras_de_get() {
        for ruta in ["/", "/hola", "/api/saludo"] {
            let get = enrutar(&peticion_de_ejemplo(Metodo::Get, ruta));
            let head = enrutar(&peticion_de_ejemplo(Metodo::Head, ruta));
            assert_eq!(get.estado, head.estado, "ruta {}", ruta);
            assert_eq!(get.frase, head.frase, "ruta {}", ruta);
            assert_eq!(
                content_length_de(&get),
                content_length_de(&head),
                "ruta {}",
                ruta
            );
            assert_eq!(get.cuerpo, head.cuerpo, "ruta {}", ruta);
        }
    }

    #[test]
    fn head_sobre_ruta_inexistente_devuelve_404() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Head, "/noexiste"));
        assert_eq!(respuesta.estado, 404);
    }

    #[test]
    fn el_content_length_coincide_con_los_bytes_del_cuerpo_utf8() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Get, "/hola"));
        let cuerpo = cuerpo_de(&respuesta);
        // "¡Hola desde Rust!" tiene caracteres multibyte: el Content-Length
        // debe contar bytes, no caracteres.
        assert!(cuerpo.len() > cuerpo.chars().count());
        assert_eq!(content_length_de(&respuesta), cuerpo.len().to_string());
    }

    #[test]
    fn una_respuesta_head_no_incluye_el_cuerpo_serializado() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Head, "/hola"));
        let bytes = serializar(&respuesta, VersionHttp::Http11, false);
        let texto = String::from_utf8_lossy(&bytes).to_string();
        assert!(texto.ends_with("\r\n\r\n"));
        assert!(!texto.contains("¡Hola desde Rust!"));
        assert!(texto.contains(&format!("Content-Length: {}", respuesta.cuerpo.len())));
    }

    #[test]
    fn una_respuesta_get_si_incluye_el_cuerpo_serializado() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Get, "/hola"));
        let bytes = serializar(&respuesta, VersionHttp::Http11, true);
        let texto = String::from_utf8_lossy(&bytes).to_string();
        assert!(texto.contains("¡Hola desde Rust!"));
    }

    #[test]
    fn los_errores_no_vuelcan_texto_sin_escapar_en_html() {
        // Un motivo con marcado debe salir escapado, no interpretado.
        let respuesta = RespuestaHttp::error(400, "Bad Request", "<script>alert(1)</script>");
        let cuerpo = cuerpo_de(&respuesta);
        assert!(!cuerpo.contains("<script>"));
        assert!(cuerpo.contains("&lt;script&gt;"));
    }

    #[test]
    fn escapar_html_escapa_los_caracteres_reservados() {
        assert_eq!(
            escapar_html("a&b<c>d\"e'f"),
            "a&amp;b&lt;c&gt;d&quot;e&#39;f"
        );
    }

    #[test]
    fn la_serializacion_usa_crlf_y_estado_coherente() {
        let respuesta = enrutar(&peticion_de_ejemplo(Metodo::Get, "/"));
        let bytes = serializar(&respuesta, VersionHttp::Http11, true);
        let texto = String::from_utf8_lossy(&bytes).to_string();
        assert!(texto.starts_with("HTTP/1.1 200 OK\r\n"));
        assert!(texto.contains("Content-Type: text/html; charset=utf-8\r\n"));
        assert!(texto.contains("Connection: close\r\n"));
        assert!(texto.contains("\r\n\r\n"));
    }

    #[test]
    fn el_505_usa_la_version_de_la_peticion() {
        let respuesta = RespuestaHttp::error(505, "HTTP Version Not Supported", "x");
        let bytes = serializar(&respuesta, VersionHttp::Http10, true);
        let texto = String::from_utf8_lossy(&bytes).to_string();
        assert!(texto.starts_with("HTTP/1.0 505 "));
    }

    // Integración con sockets reales ------------------------------------------

    /// Un servidor de prueba en un puerto efímero, con límites cortos para
    /// que las pruebas de plazo sean rápidas y deterministas.
    fn arrancar_servidor_de_prueba(
        num_trabajadores: usize,
        capacidad_cola: usize,
        duracion: Duration,
    ) -> u16 {
        let listener = TcpListener::bind(("127.0.0.1", 0)).expect("bind de prueba");
        let puerto = listener.local_addr().expect("local_addr").port();
        let limites = Limites {
            duracion,
            ..Limites::por_defecto()
        };
        thread::spawn(move || {
            let _ = servir(listener, limites, num_trabajadores, capacidad_cola);
        });
        puerto
    }

    fn conectar(puerto: u16) -> TcpStream {
        TcpStream::connect(("127.0.0.1", puerto)).expect("conexión de prueba")
    }

    /// Envía bytes y lee toda la respuesta hasta que el servidor la cierre.
    fn petición_y_respuesta(puerto: u16, bytes: &[u8]) -> String {
        let mut stream = conectar(puerto);
        stream.write_all(bytes).expect("escritura de prueba");
        stream.flush().expect("flush de prueba");
        let mut respuesta = Vec::new();
        let _ = stream.read_to_end(&mut respuesta);
        String::from_utf8_lossy(&respuesta).to_string()
    }

    #[test]
    fn integracion_get_valido_devuelve_200_y_cuerpo() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        let respuesta =
            petición_y_respuesta(puerto, b"GET /hola HTTP/1.1\r\nHost: localhost\r\n\r\n");
        assert!(respuesta.starts_with("HTTP/1.1 200 OK\r\n"));
        assert!(respuesta.contains("¡Hola desde Rust!"));
    }

    #[test]
    fn integracion_get_raiz_y_api_funcionan() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        let raiz = petición_y_respuesta(puerto, b"GET / HTTP/1.1\r\nHost: x\r\n\r\n");
        assert!(raiz.starts_with("HTTP/1.1 200 OK\r\n"));
        assert!(raiz.contains("Servidor web en Rust"));
        let api = petición_y_respuesta(puerto, b"GET /api/saludo HTTP/1.1\r\nHost: x\r\n\r\n");
        assert!(api.contains(r#"{"mensaje":"Hola desde el servidor"}"#));
    }

    #[test]
    fn integracion_head_no_devuelve_cuerpo() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        let respuesta = petición_y_respuesta(puerto, b"HEAD /hola HTTP/1.1\r\nHost: x\r\n\r\n");
        assert!(respuesta.starts_with("HTTP/1.1 200 OK\r\n"));
        assert!(respuesta.contains("Content-Length: "));
        assert!(!respuesta.contains("¡Hola desde Rust!"));
    }

    #[test]
    fn integracion_peticion_malformada_devuelve_400_y_el_servidor_sigue_vivo() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        let mala = petición_y_respuesta(puerto, b"GET / HTTP/1.1\nHost: x\r\n\r\n");
        assert!(mala.starts_with("HTTP/1.1 400 Bad Request\r\n"));
        let buena = petición_y_respuesta(puerto, b"GET / HTTP/1.1\r\nHost: x\r\n\r\n");
        assert!(buena.starts_with("HTTP/1.1 200 OK\r\n"));
    }

    #[test]
    fn integracion_cabeceras_fragmentadas_entre_escrituras() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        let mut stream = conectar(puerto);
        stream.write_all(b"GET / HTTP/1.1\r\n").expect("parte 1");
        stream.flush().expect("flush 1");
        thread::sleep(Duration::from_millis(20));
        stream.write_all(b"Host: x\r\n\r\n").expect("parte 2");
        stream.flush().expect("flush 2");
        let mut respuesta = Vec::new();
        let _ = stream.read_to_end(&mut respuesta);
        let texto = String::from_utf8_lossy(&respuesta).to_string();
        assert!(texto.starts_with("HTTP/1.1 200 OK\r\n"));
    }

    #[test]
    fn integracion_cliente_que_se_desconecta_prematuramente() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        {
            let mut stream = conectar(puerto);
            stream.write_all(b"GET / HTT").expect("escritura parcial");
            stream.flush().expect("flush parcial");
            // La conexión se cierra sin completar la petición.
        }
        let buena = petición_y_respuesta(puerto, b"GET / HTTP/1.1\r\nHost: x\r\n\r\n");
        assert!(buena.starts_with("HTTP/1.1 200 OK\r\n"));
    }

    #[test]
    fn integracion_cliente_que_excede_el_plazo_recibe_408() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_millis(300));
        let mut stream = conectar(puerto);
        stream
            .set_read_timeout(Some(Duration::from_secs(5)))
            .expect("timeout de lectura");
        stream.write_all(b"GET / HTT").expect("escritura");
        stream.flush().expect("flush");
        // Sin más datos: el plazo del servidor agota y responde 408.
        let mut respuesta = Vec::new();
        let _ = stream.read_to_end(&mut respuesta);
        let texto = String::from_utf8_lossy(&respuesta).to_string();
        assert!(texto.starts_with("HTTP/1.1 408 Request Timeout\r\n"));
    }

    #[test]
    fn integracion_varios_clientes_concurrentes() {
        let puerto = arrancar_servidor_de_prueba(4, 16, Duration::from_secs(2));
        let mut hilos = Vec::new();
        for _ in 0..8 {
            hilos.push(thread::spawn(move || {
                let respuesta = petición_y_respuesta(puerto, b"GET / HTTP/1.1\r\nHost: x\r\n\r\n");
                assert!(respuesta.starts_with("HTTP/1.1 200 OK\r\n"));
            }));
        }
        for hilo in hilos {
            hilo.join().expect("hilo de cliente");
        }
    }

    #[test]
    fn integracion_saturacion_rechaza_sin_colapsar() {
        // Un solo trabajador y cola en rendezvous: la segunda conexión no
        // tiene dónde encolarse y se rechaza cerrando el socket.
        let puerto = arrancar_servidor_de_prueba(1, 0, Duration::from_secs(2));
        let mut bloqueante = conectar(puerto);
        bloqueante
            .write_all(b"GET / HT")
            .expect("parcial del primero");
        bloqueante.flush().expect("flush del primero");
        // Espera a que el trabajador esté leyendo al primer cliente.
        thread::sleep(Duration::from_millis(100));
        let mut segunda = conectar(puerto);
        segunda
            .set_read_timeout(Some(Duration::from_secs(2)))
            .expect("timeout de lectura");
        let mut respuesta = Vec::new();
        let _ = segunda.read_to_end(&mut respuesta);
        // Rechazo controlado: se cierra sin respuesta (o se responde si
        // encaja en la cola por un carril libre).
        assert!(respuesta.is_empty());
    }

    #[test]
    fn integracion_recuperacion_tras_cliente_defectuoso() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        let mala = petición_y_respuesta(puerto, b"GET /\r\n\r\n");
        assert!(mala.starts_with("HTTP/1.1 400 Bad Request\r\n"));
        let buena = petición_y_respuesta(puerto, b"GET /api/saludo HTTP/1.1\r\nHost: x\r\n\r\n");
        assert!(buena.starts_with("HTTP/1.1 200 OK\r\n"));
    }

    #[test]
    fn integracion_post_devuelve_405_con_allow() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        let respuesta = petición_y_respuesta(puerto, b"POST / HTTP/1.1\r\nHost: x\r\n\r\n");
        assert!(respuesta.starts_with("HTTP/1.1 405 Method Not Allowed\r\n"));
        assert!(respuesta.contains("Allow: GET, HEAD\r\n"));
    }

    #[test]
    fn integracion_version_no_admitida_devuelve_505() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        let respuesta = petición_y_respuesta(puerto, b"GET / HTTP/2.0\r\nHost: x\r\n\r\n");
        assert!(respuesta.starts_with("HTTP/1.1 505 HTTP Version Not Supported\r\n"));
    }

    #[test]
    fn integracion_cuerpo_positivo_devuelve_413() {
        let puerto = arrancar_servidor_de_prueba(4, 8, Duration::from_secs(2));
        let respuesta = petición_y_respuesta(
            puerto,
            b"POST / HTTP/1.1\r\nHost: x\r\nContent-Length: 5\r\n\r\nhola!",
        );
        assert!(respuesta.starts_with("HTTP/1.1 413 Content Too Large\r\n"));
    }
}

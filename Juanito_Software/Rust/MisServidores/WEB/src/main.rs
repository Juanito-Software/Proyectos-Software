//! Servidor HTTP en Rust desde cero — solo biblioteca estándar.
//! Escucha conexiones TCP, parsea HTTP/1.x y responde.

use std::collections::HashMap;
use std::io::{BufRead, BufReader, Read, Write};
use std::net::{TcpListener, TcpStream};
use std::thread;

const PUERTO: u16 = 8080;

fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind(("0.0.0.0", PUERTO))?;
    println!("Servidor escuchando en http://127.0.0.1:{}", PUERTO);

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                thread::spawn(|| {
                    if let Err(e) = atender_cliente(stream) {
                        eprintln!("Error al atender cliente: {}", e);
                    }
                });
            }
            Err(e) => eprintln!("Error aceptando conexión: {}", e),
        }
    }
    Ok(())
}

/// Atiende una conexión: lee request, genera response y la escribe.
fn atender_cliente(mut stream: TcpStream) -> std::io::Result<()> {
    let mut reader = BufReader::new(stream.try_clone()?);
    let request = parsear_request(&mut reader)?;
    let response = manejar_request(request);
    escribir_response(&mut stream, &response)?;
    Ok(())
}

// --- Request HTTP -----------------------------------------------------------

#[derive(Debug)]
struct HttpRequest {
    metodo: String,
    path: String,
    version: String,
    headers: HashMap<String, String>,
    body: Vec<u8>,
}

fn parsear_request<R: BufRead>(reader: &mut R) -> std::io::Result<HttpRequest> {
    let mut linea_inicio = String::new();
    reader.read_line(&mut linea_inicio)?;
    let linea_inicio = linea_inicio.trim_end();
    let partes: Vec<&str> = linea_inicio.splitn(3, ' ').collect();
    let (metodo, path, version) = match partes.as_slice() {
        [m, p, v] => ((*m).to_string(), (*p).to_string(), (*v).to_string()),
        _ => {
            return Err(std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "Línea de inicio HTTP inválida",
            ));
        }
    };

    let mut headers = HashMap::new();
    loop {
        let mut linea = String::new();
        reader.read_line(&mut linea)?;
        let linea = linea.trim_end();
        if linea.is_empty() {
            break;
        }
        if let Some((nombre, valor)) = linea.split_once(": ") {
            headers.insert(
                nombre.to_lowercase().to_string(),
                valor.trim().to_string(),
            );
        }
    }

    let body = leer_body(reader, &headers)?;

    Ok(HttpRequest {
        metodo,
        path,
        version,
        headers,
        body,
    })
}

fn leer_body<R: Read>(reader: &mut R, headers: &HashMap<String, String>) -> std::io::Result<Vec<u8>> {
    let len = headers
        .get("content-length")
        .and_then(|s| s.parse::<usize>().ok())
        .unwrap_or(0);
    if len == 0 {
        return Ok(Vec::new());
    }
    let mut body = vec![0u8; len];
    reader.read_exact(&mut body)?;
    Ok(body)
}

// --- Response HTTP ----------------------------------------------------------

struct HttpResponse {
    status: u16,
    frase: String,
    headers: HashMap<String, String>,
    body: Vec<u8>,
}

impl HttpResponse {
    fn ok(body: &str) -> Self {
        let body = body.as_bytes().to_vec();
        let mut headers = HashMap::new();
        headers.insert("content-type".to_string(), "text/html; charset=utf-8".to_string());
        headers.insert("content-length".to_string(), body.len().to_string());
        Self {
            status: 200,
            frase: "OK".to_string(),
            headers,
            body,
        }
    }

    fn not_found() -> Self {
        let body = b"<h1>404 No encontrado</h1>" as &[u8];
        let body = body.to_vec();
        let mut headers = HashMap::new();
        headers.insert("content-type".to_string(), "text/html; charset=utf-8".to_string());
        headers.insert("content-length".to_string(), body.len().to_string());
        Self {
            status: 404,
            frase: "Not Found".to_string(),
            headers,
            body,
        }
    }

    fn error_interno(mensaje: &str) -> Self {
        let body = format!("<h1>500 Error interno</h1><p>{}</p>", mensaje);
        let body = body.into_bytes();
        let mut headers = HashMap::new();
        headers.insert("content-type".to_string(), "text/html; charset=utf-8".to_string());
        headers.insert("content-length".to_string(), body.len().to_string());
        Self {
            status: 500,
            frase: "Internal Server Error".to_string(),
            headers,
            body,
        }
    }
}

fn escribir_response(stream: &mut TcpStream, r: &HttpResponse) -> std::io::Result<()> {
    write!(stream, "HTTP/1.1 {} {}\r\n", r.status, r.frase)?;
    for (k, v) in &r.headers {
        write!(stream, "{}: {}\r\n", k, v)?;
    }
    write!(stream, "\r\n")?;
    stream.write_all(&r.body)?;
    stream.flush()?;
    Ok(())
}

// --- Enrutado y handlers ----------------------------------------------------

fn manejar_request(req: HttpRequest) -> HttpResponse {
    let path = req.path.split('?').next().unwrap_or(&req.path);

    match (req.metodo.as_str(), path) {
        ("GET", "/") => HttpResponse::ok(
            r#"<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Servidor Rust</title></head>
<body>
  <h1>Servidor web en Rust</h1>
  <p>Hecho desde cero, sin dependencias externas.</p>
  <p><a href="/hola">/hola</a></p>
</body>
</html>"#,
        ),
        ("GET", "/hola") => HttpResponse::ok(
            r#"<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Hola</title></head>
<body><h1>¡Hola desde Rust!</h1></body>
</html>"#,
        ),
        ("GET", "/api/saludo") => {
            let mut h = HashMap::new();
            h.insert("content-type".to_string(), "application/json; charset=utf-8".to_string());
            let body = br#"{"mensaje":"Hola desde el servidor"}"#.to_vec();
            h.insert("content-length".to_string(), body.len().to_string());
            HttpResponse {
                status: 200,
                frase: "OK".to_string(),
                headers: h,
                body,
            }
        }
        _ => HttpResponse::not_found(),
    }
}

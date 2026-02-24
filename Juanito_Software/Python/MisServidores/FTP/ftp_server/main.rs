use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, Read, Write};
use std::net::{IpAddr, Ipv4Addr, SocketAddr, TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::thread;

fn send_reply(stream: &mut TcpStream, code: u16, message: &str) -> io::Result<()> {
    let line = format!("{code} {message}\r\n");
    stream.write_all(line.as_bytes())
}

fn read_line(reader: &mut BufReader<TcpStream>) -> io::Result<Option<String>> {
    let mut buf = String::new();
    let bytes = reader.read_line(&mut buf)?;
    if bytes == 0 {
        return Ok(None);
    }
    while buf.ends_with('\n') || buf.ends_with('\r') {
        buf.pop();
    }
    Ok(Some(buf))
}

fn format_pasv_addr(ip: IpAddr, port: u16) -> String {
    let ipv4 = match ip {
        IpAddr::V4(v4) => v4,
        IpAddr::V6(_) => Ipv4Addr::new(127, 0, 0, 1),
    };
    let octets = ipv4.octets();
    let p1 = port / 256;
    let p2 = port % 256;
    format!("{},{},{},{},{},{}", octets[0], octets[1], octets[2], octets[3], p1, p2)
}

fn handle_list(data_stream: &mut TcpStream, dir: &Path) -> io::Result<()> {
    let entries = fs::read_dir(dir)?;
    for entry in entries {
        let entry = entry?;
        let meta = entry.metadata()?;
        let file_name = entry.file_name();
        let name = file_name.to_string_lossy();
        let line = if meta.is_dir() {
            format!("drwxr-xr-x 1 owner group 0 Jan 1 00:00 {name}\r\n")
        } else {
            format!("-rw-r--r-- 1 owner group {} Jan 1 00:00 {name}\r\n", meta.len())
        };
        data_stream.write_all(line.as_bytes())?;
    }
    Ok(())
}

fn handle_retr(data_stream: &mut TcpStream, path: &Path) -> io::Result<()> {
    let mut file = File::open(path)?;
    let mut buf = [0u8; 8192];
    loop {
        let n = file.read(&mut buf)?;
        if n == 0 {
            break;
        }
        data_stream.write_all(&buf[..n])?;
    }
    Ok(())
}

fn handle_stor(data_stream: &mut TcpStream, path: &Path) -> io::Result<()> {
    let mut file = File::create(path)?;
    let mut buf = [0u8; 8192];
    loop {
        let n = data_stream.read(&mut buf)?;
        if n == 0 {
            break;
        }
        file.write_all(&buf[..n])?;
    }
    Ok(())
}

fn handle_client(mut stream: TcpStream, root_dir: PathBuf) -> io::Result<()> {
    let peer = stream.peer_addr().ok();
    println!("Nueva conexion desde {:?}", peer);

    send_reply(&mut stream, 220, "Simple FTP server listo")?;

    let mut reader = BufReader::new(stream.try_clone()?);
    let mut logged_in = false;
    let mut current_dir = root_dir.clone();
    let mut last_user: Option<String> = None;
    let mut pasv_listener: Option<TcpListener> = None;

    loop {
        let line_opt = read_line(&mut reader)?;
        let line = match line_opt {
            Some(l) => l,
            None => {
                println!("Cliente desconectado {:?}", peer);
                break;
            }
        };

        let mut parts = line.splitn(2, ' ');
        let cmd = parts.next().unwrap_or("").to_uppercase();
        let arg = parts.next().map(|s| s.trim()).unwrap_or("");

        match cmd.as_str() {
            "USER" => {
                last_user = Some(arg.to_string());
                send_reply(&mut stream, 331, "Usuario OK, contrasena requerida")?;
            }
            "PASS" => {
                if last_user.is_some() {
                    logged_in = true;
                    send_reply(&mut stream, 230, "Usuario conectado")?;
                } else {
                    send_reply(&mut stream, 503, "Primero envie USER")?;
                }
            }
            "SYST" => send_reply(&mut stream, 215, "UNIX Type: L8")?,
            "PWD" => {
                let rel = current_dir
                    .strip_prefix(&root_dir)
                    .unwrap_or(Path::new(""))
                    .to_string_lossy();
                let shown = if rel.is_empty() {
                    "/".to_string()
                } else {
                    format!("/{}", rel.replace('\\', "/"))
                };
                send_reply(&mut stream, 257, &format!("\"{}\" es el directorio actual", shown))?;
            }
            "CWD" => {
                if !logged_in {
                    send_reply(&mut stream, 530, "No conectado")?;
                    continue;
                }
                let mut new_path = if arg.starts_with('/') {
                    root_dir.clone()
                } else {
                    current_dir.clone()
                };
                new_path.push(arg.trim_start_matches('/'));
                if let Ok(canon) = fs::canonicalize(&new_path) {
                    if canon.starts_with(&root_dir) && canon.is_dir() {
                        current_dir = canon;
                        send_reply(&mut stream, 250, "Directorio cambiado")?;
                    } else {
                        send_reply(&mut stream, 550, "No se puede cambiar de directorio")?;
                    }
                } else {
                    send_reply(&mut stream, 550, "No se puede cambiar de directorio")?;
                }
            }
            "TYPE" => {
                if arg.eq_ignore_ascii_case("I") {
                    send_reply(&mut stream, 200, "Modo binario")?;
                } else {
                    send_reply(&mut stream, 504, "Solo TYPE I soportado")?;
                }
            }
            "PASV" => {
                if !logged_in {
                    send_reply(&mut stream, 530, "No conectado")?;
                    continue;
                }
                let listener = TcpListener::bind("0.0.0.0:0")?;
                let local_addr = listener.local_addr()?;
                let pasv_ip = IpAddr::V4(Ipv4Addr::new(127, 0, 0, 1));
                let pasv_str = format_pasv_addr(pasv_ip, local_addr.port());
                send_reply(&mut stream, 227, &format!("Entrando en modo pasivo ({})", pasv_str))?;
                pasv_listener = Some(listener);
            }
            "LIST" => {
                if !logged_in {
                    send_reply(&mut stream, 530, "No conectado")?;
                    continue;
                }
                let listener = match pasv_listener.take() {
                    Some(l) => l,
                    None => {
                        send_reply(&mut stream, 425, "Use PASV primero")?;
                        continue;
                    }
                };
                send_reply(&mut stream, 150, "Abriendo conexion de datos para LIST")?;
                let (mut data_stream, _) = listener.accept()?;
                let target_dir = if arg.is_empty() {
                    current_dir.clone()
                } else {
                    let mut p = current_dir.clone();
                    p.push(arg);
                    p
                };
                let res = handle_list(&mut data_stream, &target_dir);
                let _ = data_stream.shutdown(std::net::Shutdown::Both);
                match res {
                    Ok(()) => send_reply(&mut stream, 226, "Transferencia completada")?,
                    Err(_) => send_reply(&mut stream, 550, "Error en LIST")?,
                }
            }
            "RETR" => {
                if !logged_in {
                    send_reply(&mut stream, 530, "No conectado")?;
                    continue;
                }
                let listener = match pasv_listener.take() {
                    Some(l) => l,
                    None => {
                        send_reply(&mut stream, 425, "Use PASV primero")?;
                        continue;
                    }
                };
                let mut path = current_dir.clone();
                path.push(arg);
                if !path.exists() || !path.is_file() {
                    send_reply(&mut stream, 550, "Archivo no existe")?;
                    continue;
                }
                send_reply(&mut stream, 150, "Abriendo conexion de datos para RETR")?;
                let (mut data_stream, _) = listener.accept()?;
                let res = handle_retr(&mut data_stream, &path);
                let _ = data_stream.shutdown(std::net::Shutdown::Both);
                match res {
                    Ok(()) => send_reply(&mut stream, 226, "Transferencia completada")?,
                    Err(_) => send_reply(&mut stream, 550, "Error en RETR")?,
                }
            }
            "STOR" => {
                if !logged_in {
                    send_reply(&mut stream, 530, "No conectado")?;
                    continue;
                }
                let listener = match pasv_listener.take() {
                    Some(l) => l,
                    None => {
                        send_reply(&mut stream, 425, "Use PASV primero")?;
                        continue;
                    }
                };
                let mut path = current_dir.clone();
                path.push(arg);
                send_reply(&mut stream, 150, "Abriendo conexion de datos para STOR")?;
                let (mut data_stream, _) = listener.accept()?;
                let res = handle_stor(&mut data_stream, &path);
                let _ = data_stream.shutdown(std::net::Shutdown::Both);
                match res {
                    Ok(()) => send_reply(&mut stream, 226, "Transferencia completada")?,
                    Err(_) => send_reply(&mut stream, 550, "Error en STOR")?,
                }
            }
            "NOOP" => send_reply(&mut stream, 200, "OK")?,
            "QUIT" => {
                send_reply(&mut stream, 221, "Adios")?;
                break;
            }
            _ => send_reply(&mut stream, 502, "Comando no implementado")?,
        }
    }

    Ok(())
}

fn main() -> io::Result<()> {
    let root_dir = std::env::current_dir()?;
    let listen_addr: SocketAddr = "0.0.0.0:2121".parse().unwrap();

    let listener = TcpListener::bind(listen_addr)?;
    println!("Servidor FTP escuchando en {}", listen_addr);
    println!("Raiz del FTP: {}", root_dir.display());

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                let root_clone = root_dir.clone();
                thread::spawn(move || {
                    if let Err(e) = handle_client(stream, root_clone) {
                        eprintln!("Error en sesion FTP: {}", e);
                    }
                });
            }
            Err(e) => eprintln!("Error aceptando conexion: {}", e),
        }
    }

    Ok(())
}

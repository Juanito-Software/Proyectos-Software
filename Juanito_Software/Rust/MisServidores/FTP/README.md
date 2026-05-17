# FTP Server en Rust

Servidor FTP básico desarrollado en Rust utilizando únicamente la biblioteca estándar (`std`).

Este programa implementa un servidor FTP funcional para pruebas locales, con canal de control y canal de datos en modo pasivo (`PASV`). Permite conectarse desde clientes FTP estándar como FileZilla para listar directorios, descargar archivos y subir archivos.

## ¿Qué hace este programa?

Este servidor escucha en `127.0.0.1:2121` y responde a comandos FTP básicos como:

- `USER` / `PASS`
- `PWD` / `CWD`
- `TYPE I`
- `PASV`
- `LIST`
- `RETR`
- `STOR`
- `NOOP`
- `QUIT`

Está pensado como proyecto educativo y de aprendizaje sobre:
- protocolos de red
- sockets TCP
- cliente/servidor
- sistema de archivos
- programación en Rust sin dependencias externas

---

## 1. Compilación (release)

```bash
cd <ruta-del-proyecto>
cargo build --release
```

El binario generado queda en `target/release/ftp_server.exe`

## 2. Ejecución del servidor

Desde PowerShell:

```powershell
cd <ruta-del-proyecto>
.\target\release\ftp_server.exe
```

Desde cmd:

```bash
cd <ruta-del-proyecto>
target\release\ftp_server.exe
```

## 3. Conexión desde cliente FTP

Ejemplo usando FileZilla:

Host: 127.0.0.1
Puerto: 2121
Usuario: cualquiera
Contraseña: cualquiera
Modo: PASV (pasivo)

---

## Estado del proyecto

- Servidor FTP funcional en entorno local
- Probado con clientes FTP estándar (FileZilla)
- Implementación sin dependencias externas
- Compilación en modo release
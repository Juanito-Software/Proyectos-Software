# Servidor Web en Rust

Servidor HTTP básico implementado en Rust utilizando únicamente la biblioteca estándar (`std`).

Este proyecto implementa un servidor web funcional para entornos locales, capaz de parsear peticiones HTTP, enrutar por método y path, y devolver respuestas HTML o JSON. No utiliza ningún crate externo.

---

## ¿Qué hace este programa?

El servidor escucha en `0.0.0.0:8080` y responde a las siguientes rutas:

| Método | Ruta | Respuesta |
|--------|------|-----------|
| GET | `/` | Página de inicio HTML |
| GET | `/hola` | Página HTML "¡Hola desde Rust!" |
| GET | `/api/saludo` | JSON `{"mensaje":"Hola desde el servidor"}` |
| Cualquier otra | — | 404 Not Found |

---

## Estructura del proyecto

```
├── Cargo.toml   # Proyecto sin dependencias externas
└── src/
    └── main.rs  # Todo el servidor en un único módulo
```

---

## Detalles de implementación

- **Concurrencia**: una conexión por hilo con `thread::spawn`
- **Parser HTTP**: lectura línea a línea con `BufReader::read_line`, división de la línea de inicio con `splitn(3, ' ')`, cabeceras con `split_once(": ")`, body con `Content-Length`
- **`HttpRequest`**: método, path, versión, mapa de cabeceras y body en bytes
- **`HttpResponse`**: constructores `ok()`, `not_found()` y `error_interno()`; escritura con `write!` y `write_all`

---

## 1. Compilación y ejecución

Con Rust instalado:

Desde cmd:

```bash
cd <ruta-del-proyecto>
cargo run

```
Desde powershell:

```powershell
cd <ruta-del-proyecto>
cargo run
```
---

## 2. Prueba en el navegador

Con el servidor en marcha, abre:

- `http://127.0.0.1:8080`
- `http://127.0.0.1:8080/hola`
- `http://127.0.0.1:8080/api/saludo`

---

## Estado del proyecto

- Servidor HTTP funcional en entorno local
- Sin dependencias externas
- Probado con navegador estándar
- Implementación educativa (no production-ready)

---

## Objetivo del proyecto

Proyecto de aprendizaje sobre:

- Protocolo HTTP a bajo nivel
- Sockets TCP en Rust
- Parseo manual de peticiones
- Arquitectura cliente-servidor
- Concurrencia básica con hilos
- Implementación de protocolo desde cero sin dependencias externas

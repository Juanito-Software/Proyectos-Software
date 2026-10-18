# Servidor Web en Rust

Servidor HTTP básico implementado en Rust utilizando únicamente la biblioteca estándar (`std`).

Este proyecto implementa un servidor web funcional para entornos locales, capaz de parsear peticiones HTTP, enrutar por método y path, y devolver respuestas HTML o JSON. No utiliza ningún crate externo.

---

## ¿Qué hace este programa?

El servidor escucha en `0.0.0.0:8080` (todas las interfaces; HTTP sin cifrar) y responde a las siguientes rutas:

| Método | Ruta | Respuesta |
|--------|------|-----------|
| GET / HEAD | `/` | Página de inicio HTML |
| GET / HEAD | `/hola` | Página HTML "¡Hola desde Rust!" |
| GET / HEAD | `/api/saludo` | JSON `{"mensaje":"Hola desde el servidor"}` |
| GET / HEAD | Cualquier otra | 404 Not Found |
| Cualquier otro método | — | 405 Method Not Allowed (`Allow: GET, HEAD`) |

Solo se admiten HTTP/1.0 y HTTP/1.1, con un único objetivo de petición por conexión (sin keep-alive ni pipelining). El cuerpo de petición no se admite: `Content-Length` positivo responde 413, `Transfer-Encoding` responde 501 y cualquier combinación ambigua de ambas cabeceras responde 400.

---

## Estructura del proyecto

```
├── Cargo.toml   # Proyecto sin dependencias externas
└── src/
    └── main.rs  # Todo el servidor en un único módulo
```

---

## Detalles de implementación

- **Concurrencia**: un conjunto fijo de trabajadores (`NUM_TRABAJADORES = 8`) con una cola acotada (`sync_channel(CAPACIDAD_COLA = 16)`); al saturarse, la conexión se rechaza cerrando el socket de forma controlada
- **Parser HTTP**: lectura de líneas byte a byte con terminador CRLF obligatorio y límites explícitos (línea de petición 8 KiB, bloque de cabeceras 16 KiB, 100 cabeceras, URI 2 KiB, plazo de 10 s); se rechazan LF aislados, CR malformados y caracteres de control
- **Validación de cabeceras**: `Vec<(nombre, valor)>` con nombres en minúsculas y duplicados conservados; se validan token de nombre, OWS en los extremos y ausencia de caracteres de control en el valor
- **`Host`**: HTTP/1.1 exige exactamente una cabecera `Host` válida (reg-name, IPv4 o IPv6 entre corchetes, puerto opcional); en HTTP/1.0 es opcional
- **Encuadre de cuerpo**: no se admiten cuerpos; `Content-Length` positivo → 413, `Transfer-Encoding` → 501, combinación ambigua → 400
- **`PeticionHttp`**: método (`GET`/`HEAD`/otro), ruta, componente de consulta, versión (`HTTP/1.0`/`HTTP/1.1`) y cabeceras validadas
- **`RespuestaHttp`**: `Content-Length` calculado en bytes (no caracteres), cabeceras en orden estable (vector, no `HashMap`), defensa contra inyección de CR/LF, `Connection: close`
- **`HEAD`**: comparte el enrutado con `GET`; omite el cuerpo pero conserva el `Content-Length` del cuerpo que habría producido `GET`
- **Errores de parsing**: mapeo explícito a 400 / 405 / 408 / 413 / 414 / 431 / 500 / 501 / 505 según el tipo de error detectado

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

# Servidor Web en Python

Servidor HTTP/1.1 escrito desde cero usando únicamente la biblioteca estándar
(`socket`, `threading`, `os`, `html`, `email.utils`). Sin frameworks ni
dependencias externas (`requirements.txt` está vacío a propósito).

Sirve archivos estáticos de `public/`, la página `/hola` y responde con las
cabeceras correctas (`Content-Length`, `Content-Type`, `Date`,
`X-Content-Type-Options: nosniff`, `Connection: close`).

**Uso local / LAN de confianza.** No está pensado para Internet: no hay TLS,
no hay keep-alive, ni HTTP/2, ni compresión, ni rango de peticiones. No envíes
información sensible por redes no fiables.

---

## Características

- `GET` y `HEAD` sobre `http://127.0.0.1:8080` (HTTP/1.0 y HTTP/1.1).
- Rutas: `/` (o `public/index.html`), `/hola` y cualquier fichero estático
  bajo `public/` (los directorios usan su `index.html`; sin él, `404`).
- Cualquier método distinto de `GET`/`HEAD` → `405` con `Allow: GET, HEAD`.
- Parseo estricto en bytes: gramática de cabeceras, Host obligatorio en
  HTTP/1.1, `Content-Length` duplicado o incompatible rechazados,
  `Transfer-Encoding` no soportado (`501`), sin cuerpos de petición (`413`).
- Envío de ficheros por bloques de 64 KiB (`Content-Length` tomado de
  `fstat`): nunca carga un archivo entero en memoria.
- Límite de clientes simultáneos (32) con semáforo; por encima responde
  `503` con cuerpo vacío y cierra.
- Plazo total de cabeceras (10 s): un cliente lento o que gotea la petición
  recibe `408` y no retiene recursos.
- Cada conexión se atiende en un hilo propio (`threading`).

### Política de rutas (seguridad)

Defensa en profundidad contra traversal y enlaces simbólicos:

- Separadores `/` y `\` normalizados por componentes; `..` que intenta salir
  de la raíz, componentes con `:` (unidades de disco, Alternate Data Streams)
  y rutas absolutas → `403`.
- Comprobación de contención con `os.path.commonpath` sobre rutas canónicas
  (no `startswith`, que engaña con prefijos como `public` vs `public_evil`).
- **Ningún enlace simbólico permitido** (ni intermedios, ni el final, ni el
  `index.html` de un directorio): política conservadora → `403`.
- Escritura de ficheros prohibida: el servidor solo abre con `O_RDONLY` y,
  donde existe, `O_NOFOLLOW` como segunda barrera.

### Límites y constantes

| Constante | Valor | Significado |
|---|---|---|
| `LIMITE_LINEA_PETICION` | 8192 B | línea de petición (sin CRLF) |
| `LIMITE_URI` | 2048 B | longitud del request-target |
| `LIMITE_CABECERAS` | 16384 B | cabeceras totales con terminador |
| `LIMITE_NUMERO_CABECERAS` | 100 | número de cabeceras |
| `LIMITE_CUERPO` | 0 | no se admiten cuerpos de petición |
| `TAMANO_BLOQUE` | 64 KiB | bloque de envío de ficheros |
| `MAX_CLIENTES_SIMULTANEOS` | 32 | permisos de hilo a la vez |
| `TIMEOUT_CONEXION` | 10 s | plazo total de cabeceras |
| `BACKLOG_CONEXIONES` | 5 | cola de `accept()` (no es límite de clientes) |

### Códigos de respuesta

| Código | Cuándo |
|---|---|
| `200` | recurso servido |
| `400` | petición malformada, Host ausente/inválido en HTTP/1.1, `Content-Length` duplicado, `Transfer-Encoding` + `Content-Length` |
| `403` | intento de salir de la raíz, enlace simbólico, permisos denegados |
| `404` | no existe, directorio sin `index.html` |
| `405` | método distinto de `GET`/`HEAD` (incluye `Allow`) |
| `408` | plazo total de cabeceras agotado |
| `413` | `Content-Length` supera `LIMITE_CUERPO` (0) |
| `414` | URI o línea de petición demasiado largas |
| `431` | cabeceras demasiado largas o demasiadas |
| `500` | error de sistema no clasificado (el detalle no se filtra al cliente) |
| `501` | `Transfer-Encoding` no soportado |
| `503` | límite de clientes simultáneos |
| `505` | versión de HTTP distinta de 1.0/1.1 |

Las páginas de error son HTML pequeño y escapan cualquier dato de la ruta
(`html.escape`); no exponen rutas absolutas del sistema.

---

## Estructura del proyecto

```
├── servidor_web.py       # El servidor completo en un único módulo
├── test_servidor_web.py  # Pruebas unitarias y de integración (unittest)
├── run.bat               # Lanzador con doble clic (usa venv/)
├── setup.bat             # Crea el venv e instala requirements.txt
├── requirements.txt      # Vacío: solo biblioteca estándar
└── public/               # Carpeta de archivos estáticos
    └── index.html
```

---

## Ejecución

Python 3.10 o superior.

```powershell
cd <ruta-del-proyecto>
python servidor_web.py
```

O con doble clic en `run.bat` (crea el venv antes con `setup.bat` si hace
falta). El servidor imprime el puerto asignado y se detiene con `Ctrl+C`.

Para servir otro directorio o puerto, edita `DIRECTORIO_RAIZ`, `HOST` y
`PUERTO` al principio de `servidor_web.py` (o llama a
`ServidorWeb(host=…, puerto=…, directorio_raiz=…)` desde tu propio script).

### Probar en el navegador

- `http://127.0.0.1:8080` → página de inicio
- `http://127.0.0.1:8080/hola` → "¡Hola desde Python!"
- `http://127.0.0.1:8080/<ruta>` → fichero de `public/` si existe

---

## Pruebas

Suite con `unittest` (stdlib): parseo, límites, seguridad de rutas,
concurrencia y cierre. Levanta el servidor real en el puerto 0 sobre un
directorio temporal; no necesita el 8080 ni recursos externos.

```powershell
python -m unittest -v test_servidor_web
```

Resultado en el desarrollo de esta versión: **110 pruebas, todas en verde**
(1 omitida en Windows: `chmod 0` no deniega lectura en NTFS).

---

## Estado y limitaciones

- Funcional y probado en local (Windows, Python 3.10+; la sintaxis es
  válida para el job `python-syntax` del CI con Python 3.12).
- **No production-ready**: sin TLS, sin keep-alive, sin autenticación, sin
  compresión, sin rangos (`Range`/`206`), sin caché (`ETag`/`304`).
- Entre la comprobación de enlaces y la apertura del fichero queda una
  ventana teórica de TOCTOU, mitigada con `O_NOFOLLOW` donde el sistema lo
  permite (en Windows no existe; ahí solo llegan rutas ya verificadas).
- Las peticiones con cuerpo se rechazan (`413`): es un servidor estático.

## Objetivo del proyecto

Proyecto de aprendizaje sobre el protocolo HTTP/1.1 a bajo nivel, sockets
TCP, parseo manual de peticiones, tipos MIME, concurrencia con hilos e
implementación de protocolo desde cero sin dependencias externas.

# FTP Server en Rust

Servidor FTP desarrollado en Rust utilizando únicamente la biblioteca estándar (`std`), sin dependencias externas.

Implementa un servidor FTP funcional para uso local y de red controlada, con canal de control y canal de datos en modo pasivo (`PASV`). Permite conectarse desde clientes FTP estándar como FileZilla para listar directorios, descargar y subir archivos. Tras el endurecimiento (confinamiento de rutas, límites, timeouts y validación de credenciales) es viable exponerlo en LAN, no en Internet público.

## Comandos soportados

- `USER` / `PASS` — autenticación (obligatoria; el servidor no arranca sin credenciales en el entorno)
- `SYST`, `TYPE I`, `PWD`, `CWD`, `NOOP`, `QUIT`
- `PASV`, `LIST`, `RETR`, `STOR`

## Configuración por variables de entorno

| Variable | Por defecto | Descripción |
| --- | --- | --- |
| `FTP_HOST` | `127.0.0.1` | IPv4 literal de escucha (no admite nombres de host). |
| `FTP_PORT` | `2121` | Puerto TCP. `0` = puerto efímero (usado por los tests). |
| `FTP_ROOT` | `storage/` junto al binario | Raíz FTP; se crea si no existe y se confina contra `..` y symlinks. |
| `FTP_USUARIO` / `FTP_CLAVE` | — | **Obligatorias**: sin ellas el servidor no arranca. |
| `FTP_MAX_CLIENTS` | `10` | Sesiones concurrentes (421 si se supera). |
| `FTP_MAX_UPLOAD_BYTES` | `52428800` (50 MiB) | Tamaño máximo de subida (`STOR`). |
| `FTP_MAX_COMMAND_BYTES` | `8192` | Máximo de bytes por línea de control (64–65536; 500 y cierre si se excede). |
| `FTP_CONTROL_TIMEOUT` | `300` | Segundos de inactividad del canal de control. |
| `FTP_DATA_CONNECT_TIMEOUT` | `10` | Segundos para aceptar la conexión de datos PASV (426 si expira). |
| `FTP_DATA_TIMEOUT` | `300` | Segundos de inactividad durante una transferencia (426 si expira). |
| `FTP_MAX_LOGIN_ATTEMPTS` | `3` | Intentos fallidos de PASS por sesión. |
| `FTP_PASV_ADDRESS` | = `FTP_HOST` | Dirección IPv4 anunciada en PASV (obligatoria si `FTP_HOST=0.0.0.0`; no puede ser `0.0.0.0`). |

En Windows (`cmd`): `set FTP_USUARIO=juan && set FTP_CLAVE=tu_clave`.
En Linux/macOS: `export FTP_USUARIO=juan FTP_CLAVE=tu_clave`.

Ejemplo de arranque completo:

```powershell
$env:FTP_USUARIO = "juan"
$env:FTP_CLAVE = "clave-secreta"
.\target\release\ftp_server.exe
```

## Compilación y ejecución

```bash
cargo build --release
# binario en target/release/ftp_server.exe (Windows) o target/release/ftp_server
```

## Conexión desde un cliente FTP

Ejemplo con FileZilla (o cualquier cliente estándar):

- Host: la dirección de `FTP_HOST` (por defecto `127.0.0.1`)
- Puerto: `FTP_PORT` (por defecto `2121`)
- Usuario / contraseña: los definidos en `FTP_USUARIO` y `FTP_CLAVE`
- Modo: PASV (pasivo)

## Notas de seguridad y límites

- **Confinamiento de rutas**: toda ruta se resuelve dentro de la raíz canónica; `..`, rutas absolutas y symlinks que salgan de la raíz se rechazan (550). `STOR` rechaza destinos que ya sean symlink. La publicación de subidas usa escritura temporal + `rename` atómico.
- **Limitación conocida (TOCTOU)**: con solo `std` no existe un equivalente portable a `openat`/`O_NOFOLLOW`, por lo que la comprobación de la raíz (`canonicalize`) y la apertura posterior del archivo no son atómicas. Está documentado como límite aceptado; mitigado, no eliminado.
- **Red**: solo IPv4 literal; el canal de datos verifica que la IP del peer coincide con la del canal de control (425 si no). No soporta modo activo (PORT) ni EPSV.
- **NAT/LAN**: si el servidor está detrás de un router/NAT, define `FTP_PASV_ADDRESS` con la dirección IP LAN que los clientes pueden alcanzar; el puerto de datos es efímero, así que el NAT debe dejar pasar el rango alto de puertos.
- Credenciales comparadas sin cortocircuito en longitud (XOR byte a byte); longitud distinta sí escapa (documentado).

## Tests

- Unitarios (en `src/main.rs`): configuración, rutas, límites, semáforo de clientes, PASV, temporal, etc.
- Integración (`tests/sesiones_ftp.rs`): arranque, login, límites, LIST/RETR/STOR, timeouts, symlinks, concurrencia. Arrancan el binario real con puerto efímero.

```bash
cargo test          # 26 unitarios + 24 de integración
cargo clippy --all-targets -- -D warnings
```

El CI del monorepo (job `Rust · tests` en `ci.yml`) ejecuta ambas suites y protege el mínimo declarado (50).

## Estado del proyecto

- Servidor FTP endurecido, sin dependencias externas
- Probado con clientes FTP estándar (FileZilla) y con la suite automatizada
- Limitaciones conocidas: TOCTOU con `std` (ver arriba), sin modo activo (PORT)

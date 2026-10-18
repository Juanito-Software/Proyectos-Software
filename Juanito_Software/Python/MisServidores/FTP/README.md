# Servidor FTP en Python

Servidor FTP básico implementado en Python utilizando únicamente la biblioteca estándar (`socket`, `threading`, `os`, `pathlib`, `tempfile`). Sin librerías FTP externas.

Este proyecto implementa un servidor FTP funcional para entornos locales, con canal de control y canal de datos en modo pasivo (`PASV`). Es compatible con clientes FTP estándar como FileZilla.

Implementación en Python como ejercicio comparativo frente a la versión en Rust.

> **Advertencia de seguridad**: FTP sin TLS transmite credenciales y datos en
> claro. `hmac.compare_digest` solo evita fallos de temporización al comparar;
> **no cifra la conexión**. Este servidor no implementa TLS/FTPS/SFTP y no
> debe exponerse a redes no confiables. Por defecto escucha solo en
> `127.0.0.1`.

---

## ¿Qué hace este programa?

El servidor escucha en `127.0.0.1:2121` y responde a comandos FTP básicos:

- `USER` / `PASS`
- `PWD` / `CWD`
- `SYST`
- `TYPE I`
- `PASV`
- `LIST`
- `RETR`
- `STOR`
- `NOOP`
- `QUIT`

La raíz FTP es el directorio `storage/` junto al script (se crea si no existe
y se puede cambiar con `FTP_ROOT`). Cualquier subdirectorio es accesible desde
el cliente FTP. Los intentos de escape de la raíz (`..`, enlaces simbólicos
hacia fuera) se rechazan.

---

## 1. Ejecución

Requiere definir las credenciales obligatorias en variables de entorno; sin
ellas el servidor no arranca:

```powershell
cd <ruta-del-proyecto>
$env:FTP_USUARIO="juan"; $env:FTP_CLAVE="tu_clave"
python servidor_ftp.py
```

Desde bash:

```bash
cd <ruta-del-proyecto>
export FTP_USUARIO=juan FTP_CLAVE=tu_clave
python servidor_ftp.py
```

No requiere instalar dependencias externas.

### Variables de entorno

| Variable | Predeterminado | Descripción |
|---|---|---|
| `FTP_HOST` | `127.0.0.1` | Interfaz de escucha. |
| `FTP_PORT` | `2121` | Puerto TCP (0 = efímero). |
| `FTP_ROOT` | `storage/` junto al script | Raíz FTP; se crea si no existe. |
| `FTP_USUARIO` | *(obligatoria)* | Usuario FTP. |
| `FTP_CLAVE` | *(obligatoria)* | Contraseña FTP. |
| `FTP_MAX_CLIENTS` | `10` | Sesiones concurrentes; el exceso recibe `421`. |
| `FTP_MAX_UPLOAD_BYTES` | `52428800` (50 MiB) | Tamaño máximo de `STOR`; el exceso da `552`. |
| `FTP_MAX_COMMAND_BYTES` | `8192` | Máximo de bytes por línea de control. |
| `FTP_DATA_CONNECT_TIMEOUT` | `10` | Segundos para abrir el canal de datos. |
| `FTP_CONTROL_TIMEOUT` | `300` | Segundos de inactividad del canal de control. |
| `FTP_MAX_LOGIN_ATTEMPTS` | `3` | Intentos fallidos de PASS por sesión. |

Los valores inválidos, negativos o fuera de rango abortan el arranque.

### Subidas STOR

`STOR` escribe en un archivo temporal del directorio de destino y solo lo
publica con `os.replace` (atómico en el mismo volumen) cuando la recepción
termina bien. Las subidas incompletas, que exceden el límite o fallan de E/S
eliminan el temporal y conservan el archivo anterior.

---

## 2. Conexión desde cliente FTP

Ejemplo usando FileZilla:

```
Host:        127.0.0.1
Puerto:      2121
Usuario:     el definido en FTP_USUARIO
Contraseña:  la definida en FTP_CLAVE
Modo:        PASV (pasivo)
```

---

## 3. Pruebas

```powershell
python -m unittest test_servidor_ftp -v
```

Las pruebas usan `unittest`, `tempfile` y sockets locales en puertos libres;
no necesitan servicios externos ni dependencias añadidas.

---

## Estado del proyecto

- Servidor FTP funcional en entorno local
- Sin dependencias externas
- Probado con clientes FTP estándar (FileZilla) y pruebas automatizadas
- Implementación educativa (no production-ready)

---

## Objetivo del proyecto

Proyecto de aprendizaje sobre:

- Protocolo FTP a bajo nivel
- Sockets TCP en Python
- Arquitectura cliente-servidor
- Concurrencia básica con hilos (`threading`)
- Implementación de protocolo desde cero sin dependencias externas

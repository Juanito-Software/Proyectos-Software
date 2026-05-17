# Servidor FTP en Python

Servidor FTP básico implementado en Python utilizando únicamente la biblioteca estándar (`socket`, `threading`, `os`, `pathlib`). Sin librerías FTP externas.

Este proyecto implementa un servidor FTP funcional para entornos locales, con canal de control y canal de datos en modo pasivo (`PASV`). Es compatible con clientes FTP estándar como FileZilla.

Implementación en Python como ejercicio comparativo frente a la versión en Rust.

---

## ¿Qué hace este programa?

El servidor escucha en `0.0.0.0:2121` y responde a comandos FTP básicos:

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

La raíz FTP es el directorio donde se encuentra el script. Cualquier subdirectorio es accesible desde el cliente FTP.

---

## 1. Ejecución

Con Python 3.10 o superior instalado:

```bash
cd <ruta-del-proyecto>
python servidor_ftp.py
```

```powershell
cd <ruta-del-proyecto>
python servidor_ftp.py
```

Desde cmd:

```bash
cd <ruta-del-proyecto>
target\release\ftp_server.exe
```

No requiere instalar dependencias externas.

---

## 2. Conexión desde cliente FTP

Ejemplo usando FileZilla:

```
Host:        127.0.0.1
Puerto:      2121
Usuario:     cualquiera
Contraseña:  cualquiera
Modo:        PASV (pasivo)
```

---

## Estado del proyecto

- Servidor FTP funcional en entorno local
- Sin dependencias externas
- Probado con clientes FTP estándar (FileZilla)
- Implementación educativa (no production-ready)

---

## Objetivo del proyecto

Proyecto de aprendizaje sobre:

- Protocolo FTP a bajo nivel
- Sockets TCP en Python
- Arquitectura cliente-servidor
- Concurrencia básica con hilos (`threading`)
- Implementación de protocolo desde cero sin dependencias externas

#!/usr/bin/env python3
"""
Servidor web HTTP/1.1 desde cero.
Solo usa la biblioteca estándar de Python (socket).
Sin dependencias externas.
"""

import socket
import threading
import os

# Configuración
HOST = "127.0.0.1"
PUERTO = 8080
DIRECTORIO_RAIZ = "public"  # Carpeta para archivos estáticos (opcional)


def parsear_peticion(datos: bytes) -> tuple[str, str, dict, bytes]:
    """
    Parsea una petición HTTP.
    Devuelve: (metodo, ruta, headers, body)
    """
    try:
        texto = datos.decode("utf-8", errors="replace")
    except Exception:
        return "GET", "/", {}, b""

    lineas = texto.replace("\r\n", "\n").split("\n")
    if not lineas:
        return "GET", "/", {}, b""

    # Línea de petición: METODO /ruta HTTP/1.x
    partes = lineas[0].split(maxsplit=2)
    metodo = partes[0] if len(partes) > 0 else "GET"
    ruta = partes[1] if len(partes) > 1 else "/"
    if "?" in ruta:
        ruta = ruta.split("?")[0]

    # Normalizar ruta: evitar path traversal
    if not ruta.startswith("/"):
        ruta = "/" + ruta
    ruta = "/" + os.path.normpath(ruta).replace("\\", "/").strip("/") if ruta != "/" else "/"

    # Headers
    headers = {}
    i = 1
    while i < len(lineas) and lineas[i]:
        if ":" in lineas[i]:
            clave, _, valor = lineas[i].partition(":")
            headers[clave.strip().lower()] = valor.strip()
        i += 1
    i += 1  # Línea en blanco antes del body

    # Body (resto)
    body = "\n".join(lineas[i:]).encode("utf-8", errors="replace") if i < len(lineas) else b""

    return metodo, ruta, headers, body


def construir_respuesta(
    codigo: int,
    razon: str,
    cuerpo: bytes,
    tipo_contenido: str = "text/html; charset=utf-8",
    cabeceras_extra: dict | None = None,
) -> bytes:
    """Construye una respuesta HTTP/1.1 en bytes."""
    cabeceras_extra = cabeceras_extra or {}
    lineas = [
        f"HTTP/1.1 {codigo} {razon}",
        f"Content-Type: {tipo_contenido}",
        f"Content-Length: {len(cuerpo)}",
        "Connection: close",
    ]
    for k, v in cabeceras_extra.items():
        lineas.append(f"{k}: {v}")
    return "\r\n".join(lineas).encode("utf-8") + b"\r\n\r\n" + cuerpo


def obtener_tipo_mime(ruta: str) -> str:
    """Tipos MIME básicos por extensión."""
    extensiones = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".ico": "image/x-icon",
        ".svg": "image/svg+xml",
        ".txt": "text/plain; charset=utf-8",
    }
    _, ext = os.path.splitext(ruta)
    return extensiones.get(ext.lower(), "application/octet-stream")


def servir_archivo(ruta: str) -> tuple[int, bytes, str]:
    """
    Intenta servir un archivo del directorio raíz.
    Devuelve: (codigo, cuerpo, tipo_contenido)
    """
    if not os.path.isdir(DIRECTORIO_RAIZ):
        return 404, b"", "text/html; charset=utf-8"

    path_fs = ruta if ruta != "/" else "/index.html"
    path_fs = path_fs.lstrip("/")
    path_completo = os.path.join(DIRECTORIO_RAIZ, path_fs)
    path_completo = os.path.normpath(path_completo)

    # Evitar salir del directorio raíz
    raiz_abs = os.path.abspath(DIRECTORIO_RAIZ)
    if not os.path.abspath(path_completo).startswith(raiz_abs):
        return 403, b"", "text/html; charset=utf-8"

    if os.path.isdir(path_completo):
        path_completo = os.path.join(path_completo, "index.html")

    if not os.path.isfile(path_completo):
        return 404, b"", "text/html; charset=utf-8"

    try:
        with open(path_completo, "rb") as f:
            cuerpo = f.read()
    except OSError:
        return 500, b"", "text/html; charset=utf-8"

    tipo = obtener_tipo_mime(path_completo)
    return 200, cuerpo, tipo


def manejar_peticion(metodo: str, ruta: str, headers: dict, body: bytes) -> bytes:
    """
    Procesa la petición y devuelve la respuesta HTTP en bytes.
    """
    html_inicio = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Servidor desde cero</title>
</head>
<body>
    <h1>Servidor web en Python</h1>
    <p>Hecho desde cero con <code>socket</code>. Sin librerias externas.</p>
    <p>Ruta solicitada: """.encode("utf-8")

    html_fin = """</p>
</body>
</html>""".encode("utf-8")

    if metodo != "GET" and metodo != "HEAD":
        cuerpo = html_inicio + f"<em>{ruta}</em> - Metodo no permitido".encode("utf-8") + html_fin
        return construir_respuesta(405, "Method Not Allowed", cuerpo)

    if ruta == "/hola":
        cuerpo = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Hola</title>
</head>
<body>
    <h1>Hola desde Python</h1>
</body>
</html>""".encode("utf-8")
        return construir_respuesta(200, "OK", cuerpo)

    codigo, cuerpo, tipo = servir_archivo(ruta)

    if codigo == 404:
        cuerpo = html_inicio + ruta.encode("utf-8") + " - No encontrado".encode("utf-8") + html_fin
        return construir_respuesta(404, "Not Found", cuerpo, tipo_contenido=tipo)
    if codigo == 403:
        cuerpo = html_inicio + "Acceso denegado".encode("utf-8") + html_fin
        return construir_respuesta(403, "Forbidden", cuerpo, tipo_contenido=tipo)
    if codigo == 500:
        cuerpo = html_inicio + "Error del servidor".encode("utf-8") + html_fin
        return construir_respuesta(500, "Internal Server Error", cuerpo, tipo_contenido=tipo)

    if metodo == "HEAD":
        cuerpo = b""
    return construir_respuesta(200, "OK", cuerpo, tipo_contenido=tipo)


def atender_cliente(conn: socket.socket, addr: tuple):
    """Atiende a un cliente en un hilo."""
    try:
        conn.settimeout(10.0)
        datos = b""
        while True:
            try:
                trozo = conn.recv(4096)
                if not trozo:
                    break
                datos += trozo
                if b"\r\n\r\n" in datos or b"\n\n" in datos:
                    break
            except socket.timeout:
                break

        if not datos:
            conn.close()
            return

        metodo, ruta, headers, body = parsear_peticion(datos)
        respuesta = manejar_peticion(metodo, ruta, headers, body)
        conn.sendall(respuesta)
    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        try:
            conn.close()
        except OSError:
            pass


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PUERTO))
    servidor.listen(5)
    print(f"Servidor en http://{HOST}:{PUERTO}")
    print("Solo biblioteca estandar (socket). Sin dependencias externas.")
    print("Detener con Ctrl+C.\n")

    try:
        while True:
            conn, addr = servidor.accept()
            hilo = threading.Thread(target=atender_cliente, args=(conn, addr))
            hilo.daemon = True
            hilo.start()
    except KeyboardInterrupt:
        print("\nApagando servidor...")
    finally:
        servidor.close()


if __name__ == "__main__":
    main()

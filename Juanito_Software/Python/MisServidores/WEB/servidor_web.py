# Copyright (C) 2025 JuanitoSoftware
#
# Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo
# los términos de la Licencia Pública General de GNU publicada por la Free
# Software Foundation, ya sea la versión 3 de la Licencia o (según tu elección)
# cualquier versión posterior.
#
# Este programa se distribuye con la esperanza de que sea útil, pero SIN
# NINGUNA GARANTÍA; incluso sin la garantía implícita de COMERCIALIZACIÓN o
# IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulta la Licencia Pública General
# de GNU para más detalles.
#
# Deberías haber recibido una copia de la Licencia Pública General de GNU junto
# con este programa. Si no es así, visita <https://www.gnu.org/licenses/>.

#!/usr/bin/env python3
"""
Servidor web HTTP/1.1 mínimo sobre la biblioteca estándar (socket, threading,
os). Sin dependencias externas y sin frameworks.

Características:
- Métodos GET y HEAD, la ruta /hola y archivos estáticos bajo una raíz web.
- Parsing estricto en bytes, con límites de tamaño y plazo total de cabeceras.
- Contención de rutas por componentes más ruta canónica; política conservadora
  que rechaza los enlaces simbólicos presentes en la ruta de acceso.
- Respuesta con Connection: close: no hay conexiones persistentes, cada
  conexión atiende una sola petición.

Aviso de seguridad: el servidor habla HTTP sin TLS. No debe usarse para
transmitir información sensible por redes no confiables, y no se considera
apto para producción sin una evaluación adicional de su modelo de amenazas.
"""

import errno
import html
import os
import re
import socket
import stat as stat_mod
import sys
import threading
import time
import urllib.parse
from email.utils import formatdate
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

HOST = "127.0.0.1"
PUERTO = 8080
DIRECTORIO_RAIZ = "public"  # Carpeta para archivos estáticos (opcional)

# Límites de recursos. Se validan al arrancar (ver validar_configuracion).
MAX_CLIENTES_SIMULTANEOS = 32   # permisos de hilo abiertos a la vez
BACKLOG_CONEXIONES = 5          # cola de accept(); no es un límite de clientes
TIMEOUT_CONEXION = 10.0         # segundos: plazo total de cabeceras y timeout
LIMITE_LINEA_PETICION = 8 * 1024   # bytes de la línea de petición (sin CRLF)
LIMITE_URI = 2048                  # bytes del destino (request-target)
LIMITE_CABECERAS = 16 * 1024       # bytes totales de cabeceras con terminador
LIMITE_NUMERO_CABECERAS = 100      # cabeceras (la línea de petición no cuenta)
LIMITE_CUERPO = 0                  # el servidor no admite cuerpos de petición
TAMANO_BLOQUE = 64 * 1024          # bytes por bloque al enviar archivos

# Frases de estado que este servidor puede emitir.
FRASES_ESTADO = {
    200: "OK",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    413: "Content Too Large",
    414: "URI Too Long",
    431: "Request Header Fields Too Large",
    500: "Internal Server Error",
    501: "Not Implemented",
    503: "Service Unavailable",
    505: "HTTP Version Not Supported",
}

# Mensajes fijos de las páginas de error. Nunca se inserta en ellos ningún
# dato procedente de la petición salvo la ruta, que se escapa con html.escape.
MENSAJES_ERROR = {
    400: "La solicitud está mal formada.",
    403: "Acceso denegado por la política de rutas del servidor.",
    404: "El recurso solicitado no existe.",
    405: "Método no admitido: solo se admiten GET y HEAD.",
    408: "El cliente tardó demasiado en completar la solicitud.",
    413: "El contenido de la solicitud supera el límite permitido.",
    414: "La dirección solicitada es demasiado larga.",
    431: "Las cabeceras de la solicitud son demasiado grandes.",
    500: "Error interno del servidor.",
    501: "Funcionalidad de protocolo no soportada por este servidor.",
    503: "Servidor ocupado: demasiados clientes simultáneos.",
    505: "Versión HTTP no soportada.",
}

PAGINA_HOLA = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Hola</title>
</head>
<body>
    <h1>Hola desde Python</h1>
</body>
</html>""".encode("utf-8")

# Errores de sistema que indican que el recurso no existe o no es servible.
_CODIGOS_ERRNO_404 = {
    errno.ENOENT,
    errno.ENOTDIR,
    errno.ENAMETOOLONG,
    errno.EINVAL,  # Windows: nombre de fichero no válido (p. ej. demasiado largo)
}
# Errores de sistema que indican acceso denegado (política o permisos).
_CODIGOS_ERRNO_403 = {
    errno.EACCES,
    errno.EPERM,
    errno.ELOOP,
}

_TOKEN = re.compile(rb"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")
_VERSION = re.compile(rb"^HTTP/([0-9]+)\.([0-9]+)$")
_NUMERICO = re.compile(r"^[0-9]+$")
_ESCAPE_VALIDO = re.compile(rb"%(?![0-9A-Fa-f]{2})")
_HOST = re.compile(
    r"^(?:[A-Za-z0-9._~%!$&'()+,;=-]+|\[[0-9A-Fa-f:.]+\])(?::([0-9]{1,5}))?$"
)


class ErrorPeticion(Exception):
    """Solicitud inválida: `codigo` es el código HTTP que debe responderse.

    `parcial` guarda los bytes recibidos hasta el fallo para poder detectar si
    la petición era HEAD (y no enviar cuerpo en el error).
    """

    def __init__(self, codigo: int, parcial: bytes = b""):
        super().__init__(f"HTTP {codigo} {FRASES_ESTADO[codigo]}")
        self.codigo = codigo
        self.parcial = parcial


class _ClienteInactivo(Exception):
    """El cliente cerró o no envió nada: se cierra sin respuesta."""


class Peticion(NamedTuple):
    """Petición HTTP ya validada."""
    metodo: str
    ruta: str
    cabeceras: dict
    version: tuple


class Respuesta:
    """Respuesta HTTP pendiente de enviar: un cuerpo en memoria o un fichero."""

    def __init__(self, codigo, razon, tipo, cuerpo=None, ruta_archivo=None,
                 cabeceras=None):
        if cuerpo is None and ruta_archivo is None:
            raise ValueError("la respuesta necesita cuerpo o ruta_archivo")
        self.codigo = codigo
        self.razon = razon
        self.tipo = tipo
        self.cuerpo = cuerpo
        self.ruta_archivo = ruta_archivo
        self.cabeceras = cabeceras or {}


def validar_configuracion(host, puerto, directorio_raiz, max_clientes,
                          timeout_conexion, backlog) -> str:
    """Valida la configuración de arranque y devuelve la raíz canónica.

    Lanza ValueError con un mensaje para el operador (nunca llega al cliente).
    """
    if not isinstance(host, str) or not host:
        raise ValueError("host no puede estar vacío")
    if not isinstance(puerto, int) or isinstance(puerto, bool) or not 0 <= puerto <= 65535:
        raise ValueError(f"puerto fuera de rango: {puerto!r}")
    if not isinstance(max_clientes, int) or isinstance(max_clientes, bool) or max_clientes < 1:
        raise ValueError(f"max_clientes debe ser >= 1: {max_clientes!r}")
    if not isinstance(timeout_conexion, (int, float)) or isinstance(timeout_conexion, bool) \
            or timeout_conexion <= 0:
        raise ValueError(f"timeout_conexion debe ser > 0: {timeout_conexion!r}")
    if not isinstance(backlog, int) or isinstance(backlog, bool) or backlog < 1:
        raise ValueError(f"backlog debe ser >= 1: {backlog!r}")

    limites = {
        "LIMITE_LINEA_PETICION": (LIMITE_LINEA_PETICION, 1),
        "LIMITE_URI": (LIMITE_URI, 1),
        "LIMITE_CABECERAS": (LIMITE_CABECERAS, 1),
        "LIMITE_NUMERO_CABECERAS": (LIMITE_NUMERO_CABECERAS, 1),
        "LIMITE_CUERPO": (LIMITE_CUERPO, 0),
        "TAMANO_BLOQUE": (TAMANO_BLOQUE, 1),
    }
    for nombre, (valor, minimo) in limites.items():
        if not isinstance(valor, int) or isinstance(valor, bool) or valor < minimo:
            raise ValueError(f"{nombre} debe ser >= {minimo}: {valor!r}")
    if LIMITE_URI >= LIMITE_LINEA_PETICION:
        raise ValueError("LIMITE_URI debe ser menor que LIMITE_LINEA_PETICION")
    if LIMITE_LINEA_PETICION > LIMITE_CABECERAS:
        raise ValueError("LIMITE_LINEA_PETICION no puede superar LIMITE_CABECERAS")

    raiz = os.path.realpath(directorio_raiz)
    if not os.path.isdir(raiz):
        raise ValueError(
            f"el directorio raíz no existe o no es un directorio: {directorio_raiz!r}"
        )
    return raiz


def _buscar_terminador(datos: bytes):
    """Posición y longitud del terminador de cabeceras, o None si no está."""
    candidatas = []
    pos = datos.find(b"\r\n\r\n")
    if pos != -1:
        candidatas.append((pos, 4))
    pos = datos.find(b"\n\n")
    if pos != -1:
        candidatas.append((pos, 2))
    if not candidatas:
        return None
    return min(candidatas)


def leer_bloque_cabeceras(sock: socket.socket, timeout: float):
    """Lee bytes hasta el terminador de cabeceras con plazo total.

    Devuelve (bloque sin terminador, sobrante). Acota la memoria y el tiempo:
    jamás acumula datos sin límite esperando el terminador.
    """
    datos = b""
    inicio = time.monotonic()
    while True:
        restante = timeout - (time.monotonic() - inicio)
        if restante <= 0:
            if not datos:
                raise _ClienteInactivo()
            raise ErrorPeticion(408, datos)
        try:
            sock.settimeout(restante)
            trozo = sock.recv(4096)
        except (socket.timeout, TimeoutError):
            if not datos:
                raise _ClienteInactivo()
            raise ErrorPeticion(408, datos)
        if not trozo:
            # El cliente cerró a mitad de la solicitud: no se completa y
            # tampoco se interpreta como una petición válida.
            if not datos:
                raise _ClienteInactivo()
            raise ErrorPeticion(400, datos)
        datos += trozo

        terminador = _buscar_terminador(datos)
        if terminador is not None:
            fin, longitud = terminador
            bloque = datos[:fin]
            if len(bloque) + longitud > LIMITE_CABECERAS:
                raise ErrorPeticion(431, bloque)
            return bloque, datos[fin + longitud:]

        # Sin terminador aún: acotar línea de petición y total de cabeceras.
        salto = datos.find(b"\n")
        if salto < 0:
            if len(datos) > LIMITE_LINEA_PETICION:
                raise ErrorPeticion(414, datos)
        elif salto > LIMITE_LINEA_PETICION:
            raise ErrorPeticion(414, datos)
        if len(datos) > LIMITE_CABECERAS:
            raise ErrorPeticion(431, datos)


def _decodificar_ruta(ruta: bytes) -> str:
    """Decodifica el porcentaje de la ruta y valida que sea texto UTF-8."""
    if _ESCAPE_VALIDO.search(ruta):
        raise ErrorPeticion(400)
    try:
        texto = urllib.parse.unquote_to_bytes(ruta).decode("utf-8")
    except UnicodeDecodeError:
        raise ErrorPeticion(400) from None
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in texto):
        raise ErrorPeticion(400)
    return texto


def _host_valido(valor: str) -> bool:
    """Valida un valor Host: nombre, IPv4, IPv6 entre corchetes y puerto."""
    if not valor or len(valor) > 255:
        return False
    coincidencia = _HOST.match(valor)
    if coincidencia is None:
        return False
    puerto = coincidencia.group(1)
    return not (puerto and int(puerto) > 65535)


def parsear_peticion(bloque: bytes) -> Peticion:
    """Valida un bloque de cabeceras completo (bytes) y devuelve la petición.

    Lanza ErrorPeticion ante cualquier desviación de la gramática. Nunca
    reinterpreta una solicitud inválida como GET / y no decodifica bytes
    arbitrarios como texto salvo tras validarlos.
    """
    if not bloque:
        raise ErrorPeticion(400)
    if b"\r" in bloque.replace(b"\r\n", b""):
        raise ErrorPeticion(400)

    lineas = [l[:-1] if l.endswith(b"\r") else l for l in bloque.split(b"\n")]
    if len(lineas) > 1 and lineas[-1] == b"":
        # Se tolera un único salto final tras la última cabecera; una línea
        # en blanco intermedia sigue rechazándose en el bucle de abajo.
        lineas.pop()
    if len(lineas) - 1 > LIMITE_NUMERO_CABECERAS:
        raise ErrorPeticion(431)

    linea_peticion = lineas[0]
    if len(linea_peticion) > LIMITE_LINEA_PETICION:
        raise ErrorPeticion(414)
    partes = linea_peticion.split(b" ")
    if len(partes) != 3 or not all(partes):
        raise ErrorPeticion(400)
    metodo_b, destino_b, version_b = partes
    if not _TOKEN.fullmatch(metodo_b):
        raise ErrorPeticion(400)
    metodo = metodo_b.decode("ascii")

    coincidencia = _VERSION.fullmatch(version_b)
    if coincidencia is None:
        raise ErrorPeticion(400)
    version = (int(coincidencia.group(1)), int(coincidencia.group(2)))
    if version not in ((1, 0), (1, 1)):
        raise ErrorPeticion(505)

    if len(destino_b) > LIMITE_URI:
        raise ErrorPeticion(414)
    if not destino_b.startswith(b"/"):
        # Solo se admite origin-form: no hay soporte de proxy absoluto.
        raise ErrorPeticion(400)
    ruta_cruda = destino_b.partition(b"?")[0]
    ruta = _decodificar_ruta(ruta_cruda)

    cabeceras: dict = {}
    for linea in lineas[1:]:
        if not linea or linea[:1] in (b" ", b"\t"):
            raise ErrorPeticion(400)  # línea en blanco interior u obs-fold
        if b":" not in linea:
            raise ErrorPeticion(400)
        nombre_b, _, valor_b = linea.partition(b":")
        if not _TOKEN.fullmatch(nombre_b):
            raise ErrorPeticion(400)
        valor_b = valor_b.strip(b" \t")
        if any(c < 0x20 and c != 0x09 for c in valor_b) or 0x7F in valor_b:
            raise ErrorPeticion(400)
        nombre = nombre_b.decode("ascii").lower()
        valor = valor_b.decode("latin-1")
        if nombre in cabeceras:
            if nombre in ("host", "content-length"):
                raise ErrorPeticion(400)
            cabeceras[nombre] += ", " + valor
        else:
            cabeceras[nombre] = valor

    # HTTP/1.1 exige exactamente un Host válido; en HTTP/1.0 es opcional,
    # pero si aparece también se valida.
    if "host" in cabeceras:
        if not _host_valido(cabeceras["host"]):
            raise ErrorPeticion(400)
    elif version == (1, 1):
        raise ErrorPeticion(400)

    hay_te = "transfer-encoding" in cabeceras
    hay_cl = "content-length" in cabeceras
    if hay_te and hay_cl:
        # Encuadre ambiguo (smuggling): se rechaza sin interpretar nada.
        raise ErrorPeticion(400)
    if hay_te:
        # No se implementa Transfer-Encoding (chunked incluido).
        raise ErrorPeticion(501)
    if hay_cl:
        valor_cl = cabeceras["content-length"]
        if not _NUMERICO.fullmatch(valor_cl):
            raise ErrorPeticion(400)
        if int(valor_cl) > LIMITE_CUERPO:
            # El servidor no admite cuerpos: cualquier cuerpo supera el límite.
            raise ErrorPeticion(413)

    return Peticion(metodo=metodo, ruta=ruta, cabeceras=cabeceras, version=version)


def construir_cabeceras(codigo: int, razon: str, tamanyo_cuerpo: int,
                        tipo_contenido: str, cabeceras_extra=None) -> bytes:
    """Cabeceras de respuesta en bytes (terminador incluido)."""
    cabeceras_extra = cabeceras_extra or {}
    lineas = [
        f"HTTP/1.1 {codigo} {razon}",
        f"Date: {formatdate(usegmt=True)}",
        f"Content-Type: {tipo_contenido}",
        f"Content-Length: {tamanyo_cuerpo}",
        "X-Content-Type-Options: nosniff",
        "Connection: close",
    ]
    for nombre, valor in cabeceras_extra.items():
        if any(salto in nombre or salto in valor for salto in ("\r", "\n")):
            raise ValueError("cabecera extra con saltos de línea")
        lineas.append(f"{nombre}: {valor}")
    return ("\r\n".join(lineas) + "\r\n\r\n").encode("latin-1")


def construir_respuesta(codigo: int, razon: str, cuerpo: bytes,
                        tipo_contenido: str = "text/html; charset=utf-8",
                        cabeceras_extra: dict | None = None) -> bytes:
    """Respuesta HTTP/1.1 completa en bytes (para cuerpos pequeños)."""
    cabeceras = construir_cabeceras(codigo, razon, len(cuerpo),
                                    tipo_contenido, cabeceras_extra)
    return cabeceras + cuerpo


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
    _, extension = os.path.splitext(ruta)
    return extensiones.get(extension.lower(), "application/octet-stream")


def pagina_error(codigo: int, ruta: str | None = None) -> bytes:
    """Página de error pequeña; cualquier dato insertado se escapa."""
    mensaje = MENSAJES_ERROR.get(codigo, "Error.")
    bloque_ruta = ""
    if ruta is not None:
        escapada = html.escape(ruta, quote=True)
        bloque_ruta = f"<p>Ruta solicitada: <code>{escapada}</code></p>"
    plantilla = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{codigo} {razon}</title>
</head>
<body>
    <h1>{codigo} {razon}</h1>
    <p>{mensaje}</p>
    {bloque_ruta}
</body>
</html>"""
    texto = plantilla.format(codigo=codigo, razon=FRASES_ESTADO[codigo],
                             mensaje=mensaje, bloque_ruta=bloque_ruta)
    return texto.encode("utf-8")


def respuesta_error(codigo: int, ruta: str | None = None) -> Respuesta:
    """Respuesta de error coherente con su frase de estado."""
    return Respuesta(codigo, FRASES_ESTADO[codigo], "text/html; charset=utf-8",
                     cuerpo=pagina_error(codigo, ruta))


def resolver_ruta(raiz: str, ruta_url: str) -> str:
    """Resuelve una ruta de URL a una ruta de fichero dentro de la raíz.

    Defensa en varias capas: componentes propios (también con separador \\),
    rechazo de intentos de salida y de componentes con dos puntos de Windows,
    escaneo de enlaces simbólicos en cada componente intermedio y final, y
    comprobación de contención con os.path.commonpath sobre rutas canónicas.
    Lanza ErrorPeticion (400/403) cuando la política impide el acceso.
    """
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in ruta_url):
        raise ErrorPeticion(400)

    partes: list = []
    for componente in re.split(r"[/\\]", ruta_url):
        if componente in ("", "."):
            continue
        if componente == "..":
            if not partes:
                raise ErrorPeticion(403)  # intento de salir de la raíz
            partes.pop()
            continue
        if ":" in componente:
            # Unidad de disco o stream alternativo de Windows: nunca permitido.
            raise ErrorPeticion(403)
        partes.append(componente)

    actual = raiz
    for componente in partes:
        actual = os.path.join(actual, componente)
        if os.path.islink(actual):
            # Política conservadora: ningún enlace simbólico en la ruta.
            raise ErrorPeticion(403)
    destino = actual if partes else raiz

    raiz_canonica = os.path.realpath(raiz)
    if not _contenido(raiz_canonica, os.path.realpath(destino)):
        raise ErrorPeticion(403)

    if os.path.isdir(destino):
        indice = os.path.join(destino, "index.html")
        if os.path.islink(indice):
            raise ErrorPeticion(403)
        if not _contenido(raiz_canonica, os.path.realpath(indice)):
            raise ErrorPeticion(403)
        destino = indice
    return destino


def _contenido(raiz_canonica: str, ruta: str) -> bool:
    """True si `ruta` cae dentro de `raiz_canonica` por componentes de ruta."""
    try:
        comun = os.path.commonpath(
            [os.path.normcase(raiz_canonica), os.path.normcase(ruta)]
        )
    except (ValueError, OSError):
        # Distinta unidad de disco u otra imposibilidad: fuera de la raíz.
        return False
    return comun == os.path.normcase(raiz_canonica)


def _codigo_para_error_os(exc: OSError) -> int | None:
    """Traduce un error del sistema a código HTTP, o None si es interno."""
    if isinstance(exc, PermissionError):
        return 403
    if exc.errno in _CODIGOS_ERRNO_403:
        return 403
    if exc.errno in _CODIGOS_ERRNO_404:
        return 404
    return None


def abrir_archivo(ruta: str):
    """Abre un fichero para lectura sin seguimiento de enlaces finales.

    En plataformas con O_NOFOLLOW se pasa la bandera como segunda barrera
    frente a enlaces que aparezcan entre la comprobación y la apertura. Los
    errores del sistema se convierten en ErrorPeticion; los no clasificados
    se propagan para que el llamante responda 500.
    """
    if os.path.isdir(ruta):
        # En Windows abrir un directorio falla con EACCES (403); se comprueba
        # antes de abrir para responder 404 en todas las plataformas, igual
        # que servir_archivo.
        raise ErrorPeticion(404)
    banderas = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(ruta, banderas)
    except OSError as exc:
        codigo = _codigo_para_error_os(exc)
        if codigo is None:
            raise
        raise ErrorPeticion(codigo) from None
    try:
        if not stat_mod.S_ISREG(os.fstat(descriptor).st_mode):
            raise ErrorPeticion(404)
        return os.fdopen(descriptor, "rb")
    except BaseException:
        os.close(descriptor)
        raise


def servir_archivo(ruta: str, raiz: str) -> Respuesta:
    """Resuelve un archivo estático dentro de la raíz y prepara su respuesta."""
    try:
        destino = resolver_ruta(raiz, ruta)
    except ErrorPeticion as exc:
        # 400 (ruta no decodable) o 403 (fuera de la raíz o enlace simbólico);
        # la existencia se comprueba más abajo para no mezclar 404 y 403.
        return respuesta_error(exc.codigo, ruta)

    try:
        info = os.stat(destino)
    except OSError as exc:
        codigo = _codigo_para_error_os(exc)
        if codigo is not None:
            return respuesta_error(codigo, ruta)
        return respuesta_error(500)
    if stat_mod.S_ISDIR(info.st_mode):
        # Directorio sin index.html (o index.html que es un directorio).
        return respuesta_error(404, ruta)

    return Respuesta(200, FRASES_ESTADO[200], obtener_tipo_mime(destino),
                     cuerpo=None, ruta_archivo=destino)


def manejar_peticion(peticion: Peticion, raiz: str) -> Respuesta:
    """Enruta una petición válida y devuelve la respuesta correspondiente."""
    if peticion.metodo not in ("GET", "HEAD"):
        respuesta = respuesta_error(405, peticion.ruta)
        respuesta.cabeceras["Allow"] = "GET, HEAD"
        return respuesta
    if peticion.ruta == "/hola":
        return Respuesta(200, FRASES_ESTADO[200], "text/html; charset=utf-8",
                         cuerpo=PAGINA_HOLA)
    return servir_archivo(peticion.ruta, raiz)


def enviar_respuesta(sock: socket.socket, respuesta: Respuesta, metodo: str) -> None:
    """Envía cabeceras y, salvo HEAD, el cuerpo (archivos por bloques).

    Content-Length sale de len(cuerpo) o del tamaño en disco obtenido con
    fstat tras abrir: coincide siempre con los bytes que se anuncian. Nunca
    se carga un archivo entero en memoria. Si el fichero cambia durante el
    envío se transmiten como mucho los `tamanyo` anunciados; si se recorta,
    la conexión se cierra con el cuerpo incompleto y el cliente lo detecta
    porque la conexión va con Connection: close.
    """
    archivo = None
    if respuesta.ruta_archivo is not None:
        try:
            archivo = abrir_archivo(respuesta.ruta_archivo)
        except ErrorPeticion as exc:
            respuesta = respuesta_error(exc.codigo)
        except OSError:
            respuesta = respuesta_error(500)
    try:
        if archivo is not None:
            tamanyo = os.fstat(archivo.fileno()).st_size
        else:
            tamanyo = len(respuesta.cuerpo or b"")
        sock.sendall(construir_cabeceras(respuesta.codigo, respuesta.razon,
                                         tamanyo, respuesta.tipo,
                                         respuesta.cabeceras))
        if metodo == "HEAD":
            return
        if archivo is not None:
            restantes = tamanyo
            while restantes > 0:
                trozo = archivo.read(min(TAMANO_BLOQUE, restantes))
                if not trozo:
                    break
                sock.sendall(trozo)
                restantes -= len(trozo)
        elif respuesta.cuerpo:
            sock.sendall(respuesta.cuerpo)
    finally:
        if archivo is not None:
            archivo.close()


def _responder_error(sock: socket.socket, codigo: int, parcial: bytes) -> None:
    """Responde un error respetando HEAD si la petición parcial lo delata."""
    es_head = parcial[:5] == b"HEAD "
    try:
        enviar_respuesta(sock, respuesta_error(codigo), "HEAD" if es_head else "GET")
    except OSError:
        pass


def atender_cliente(conn: socket.socket, addr: tuple, servidor: "ServidorWeb") -> None:
    """Atiende una única petición en el hilo actual y cierra el socket.

    `addr` se conserva para diagnósticos del llamante; aquí no se usa.
    """
    try:
        conn.settimeout(servidor.timeout_conexion)
        try:
            bloque, _sobrante = leer_bloque_cabeceras(conn, servidor.timeout_conexion)
        except _ClienteInactivo:
            return
        except ErrorPeticion as exc:
            _responder_error(conn, exc.codigo, exc.parcial)
            return
        try:
            peticion = parsear_peticion(bloque)
        except ErrorPeticion as exc:
            _responder_error(conn, exc.codigo, bloque)
            return
        respuesta = manejar_peticion(peticion, servidor.raiz)
        enviar_respuesta(conn, respuesta, peticion.metodo)
    except (ConnectionResetError, BrokenPipeError, TimeoutError, OSError):
        pass
    finally:
        try:
            conn.close()
        except OSError:
            pass


class ServidorWeb:
    """Servidor HTTP/1.1 con límite de clientes simultáneos.

    El límite se toma como permiso de un BoundedSemaphore antes de crear el
    hilo y se libera siempre en un finally. `listen()` solo dimensiona la
    cola de conexiones pendientes, no la concurrencia.
    """

    def __init__(self, host=HOST, puerto=PUERTO, directorio_raiz=DIRECTORIO_RAIZ,
                 max_clientes=MAX_CLIENTES_SIMULTANEOS,
                 timeout_conexion=TIMEOUT_CONEXION,
                 backlog=BACKLOG_CONEXIONES):
        self.raiz = validar_configuracion(host, puerto, directorio_raiz,
                                          max_clientes, timeout_conexion, backlog)
        self.host = host
        self.puerto = puerto
        self.max_clientes = max_clientes
        self.timeout_conexion = timeout_conexion
        self.backlog = backlog
        self.puerto_asignado: int | None = None
        self._permisos = threading.BoundedSemaphore(max_clientes)
        self._socket: socket.socket | None = None
        self._deteniendo = threading.Event()

    def arrancar(self) -> int:
        """Abre y escucha el socket; devuelve el puerto asignado."""
        if self._socket is not None:
            raise RuntimeError("el servidor ya está arrancado")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.puerto))
            sock.listen(self.backlog)
        except BaseException:
            sock.close()
            raise
        self._socket = sock
        self.puerto_asignado = sock.getsockname()[1]
        return self.puerto_asignado

    def servir_bucle(self) -> None:
        """Bucle de aceptación: un hilo y un permiso por conexión."""
        sock = self._socket
        if sock is None:
            raise RuntimeError("el servidor no está arrancado")
        while not self._deteniendo.is_set():
            try:
                conn, addr = sock.accept()
            except OSError:
                if self._deteniendo.is_set():
                    break
                # Error transitorio del socket: no se apaga el servidor.
                time.sleep(0.01)
                continue
            if not self._permisos.acquire(blocking=False):
                # Límite alcanzado: rechazo limpio con Content-Length: 0 para
                # que la respuesta sea válida también si era HEAD (no se lee
                # la petición, así que no se puede inspeccionar el método).
                try:
                    conn.settimeout(2.0)
                    conn.sendall(construir_respuesta(
                        503, FRASES_ESTADO[503], b""))
                except OSError:
                    pass
                finally:
                    try:
                        conn.close()
                    except OSError:
                        pass
                continue
            try:
                threading.Thread(target=self._atender_con_permiso,
                                 args=(conn, addr), daemon=True).start()
            except BaseException:
                # Si el hilo no arranca, se devuelve el permiso y se cierra.
                self._permisos.release()
                try:
                    conn.close()
                except OSError:
                    pass
                print(f"No se pudo iniciar un hilo para {addr}: "
                      f"{sys.exc_info()[1]}", file=sys.stderr)

    def _atender_con_permiso(self, conn: socket.socket, addr: tuple) -> None:
        try:
            atender_cliente(conn, addr, self)
        finally:
            try:
                conn.close()
            except OSError:
                pass
            self._permisos.release()

    def detener(self) -> None:
        """Cierra el socket de escucha y marca el fin del bucle."""
        self._deteniendo.set()
        sock, self._socket = self._socket, None
        if sock is not None:
            # En Linux, close() desde otro hilo NO despierta un accept()
            # bloqueado: el hilo de servir_bucle se quedaría colgado. shutdown()
            # sí lo despierta (accept() falla con EINVAL). En Windows, close()
            # ya basta y shutdown() sobre un socket de escucha lanza OSError,
            # que se ignora.
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass


def main() -> int:
    """Arranque desde consola: valida, escucha y espera Ctrl+C."""
    try:
        servidor = ServidorWeb()
    except ValueError as exc:
        print(f"Configuración inválida: {exc}", file=sys.stderr)
        return 2
    try:
        servidor.arrancar()
    except OSError as exc:
        print(f"No se pudo escuchar en {servidor.host}:{servidor.puerto}: "
              f"{exc.strerror or exc}", file=sys.stderr)
        return 1
    print(f"Servidor en http://{servidor.host}:{servidor.puerto_asignado}")
    print(f"Raíz web: {servidor.raiz}")
    print("Solo biblioteca estandar (socket). Sin dependencias externas.")
    print("AVISO: HTTP sin TLS; no envíes información sensible por redes no "
          "fiables.")
    print("Detener con Ctrl+C.\n")
    try:
        servidor.servir_bucle()
    except KeyboardInterrupt:
        print("\nApagando servidor...")
    finally:
        servidor.detener()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
Servidor FTP implementado desde cero.
Solo biblioteca estándar: socket, threading, os, tempfile, pathlib.
Sin librerías FTP externas.

ADVERTENCIA DE SEGURIDAD
========================
Este servidor NO implementa TLS/FTPS/SFTP: las credenciales (USER/PASS) y
todo el contenido transferido viajan en claro por la red. hmac.compare_digest
solo evita fallos de temporización al comparar credenciales; NO cifra nada.
Use este servidor únicamente en entornos locales o redes de confianza.

Configuración por variables de entorno (todas opcionales salvo credenciales):

  FTP_HOST                  Escucha. Por defecto 127.0.0.1 (no exponerlo a
                            redes no confiables).
  FTP_PORT                  Puerto TCP. Por defecto 2121. 0 = puerto efímero
                            (útil para pruebas; el puerto real se registra
                            en el log).
  FTP_ROOT                  Raíz FTP. Por defecto el directorio "storage"
                            junto al script. Se crea si no existe y se
                            resuelve UNA sola vez al arrancar.
  FTP_USUARIO / FTP_CLAVE   Credenciales. OBLIGATORIAS; sin ellas no arranca.
  FTP_MAX_CLIENTS           Sesiones concurrentes máximas. Por defecto 10.
  FTP_MAX_UPLOAD_BYTES      Tamaño máximo de subida (STOR). Por defecto
                            52428800 (50 MiB).
  FTP_MAX_COMMAND_BYTES     Máximo de bytes por línea de control.
                            Por defecto 8192.
  FTP_DATA_CONNECT_TIMEOUT  Segundos para establecer el canal de datos PASV.
                            Por defecto 10.
  FTP_CONTROL_TIMEOUT       Segundos de inactividad del canal de control.
                            Por defecto 300.
  FTP_MAX_LOGIN_ATTEMPTS    Intentos fallidos de PASS por sesión antes de
                            cerrar la conexión. Por defecto 3.

GARANTÍAS DE FILESYSTEM (y sus límites)
========================================
- Las rutas se resuelven contra la raíz virtual "/" y se validan con
  Path.resolve() + is_relative_to() (nunca startswith): los intentos de
  escape con ".." o separadores alternativos se rechazan.
- Se sigue la política "resolve y comparar por componentes". Esto NO es una
  protección absoluta frente a carreras TOCTOU: entre la validación y la
  apertura, un atacante con permisos de escritura en la raíz podría
  sustituir componentes por enlaces simbólicos. Operaciones basadas en
  descriptores de directorio (openat/O_NOFOLLOW) ofrecerían mayor garantía
  pero no están disponibles de forma portable en la stdlib de Windows; aquí
  no se usan y la limitación queda documentada.
- STOR usa un archivo temporal creado con mkstemp (O_EXCL) en el directorio
  de destino y lo publica con os.replace (atómico en el mismo volumen,
  NTFS/POSIX). Las subidas incompletas NUNCA reemplazan el archivo previo.
- Diferencias POSIX/Windows: os.replace es atómico en ambos; O_NOFOLLOW no
  existe en Windows; los enlaces simbólicos en Windows requieren privilegios
  y Path.is_symlink() los detecta en NTFS. La protección frente a symlink
  en destino de escritura es best-effort en Windows.
- Durabilidad: se hace flush()+fsync() antes de publicar; el directorio no
  se sincroniza (fsync de directorio no es portable en Windows), por lo que
  tras un corte de energía el nombre podría perderse aunque el contenido
  esté en disco.
"""

import hmac
import logging
import os
import socket
import tempfile
import threading
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuración centralizada (leída del entorno y validada al importar)
# ---------------------------------------------------------------------------


def _entorno_entero(nombre: str, predeterminado: int, minimo: int | None = None,
                    maximo: int | None = None) -> int:
    """Lee un entero del entorno validando rango; aborta si es inválido."""
    valor = os.environ.get(nombre)
    if valor is None or valor == "":
        return predeterminado
    try:
        v = int(valor)
    except ValueError:
        raise SystemExit(f"Valor inválido para {nombre}: '{valor}' debe ser un entero")
    if minimo is not None and v < minimo:
        raise SystemExit(f"Valor inválido para {nombre}: {v} debe ser >= {minimo}")
    if maximo is not None and v > maximo:
        raise SystemExit(f"Valor inválido para {nombre}: {v} debe ser <= {maximo}")
    return v


def _entorno_cadena(nombre: str, predeterminado: str) -> str:
    """Lee una cadena del entorno."""
    return os.environ.get(nombre, predeterminado)


FTP_HOST = _entorno_cadena("FTP_HOST", "127.0.0.1")
FTP_PORT = _entorno_entero("FTP_PORT", 2121, minimo=0, maximo=65535)
FTP_ROOT = _entorno_cadena("FTP_ROOT", str(Path(__file__).resolve().parent / "storage"))
FTP_USUARIO = _entorno_cadena("FTP_USUARIO", "")
FTP_CLAVE = _entorno_cadena("FTP_CLAVE", "")
FTP_MAX_CLIENTS = _entorno_entero("FTP_MAX_CLIENTS", 10, minimo=1, maximo=1000)
FTP_MAX_UPLOAD_BYTES = _entorno_entero("FTP_MAX_UPLOAD_BYTES", 50 * 1024 * 1024, minimo=1)
FTP_MAX_COMMAND_BYTES = _entorno_entero("FTP_MAX_COMMAND_BYTES", 8192, minimo=64, maximo=65536)
FTP_DATA_CONNECT_TIMEOUT = _entorno_entero("FTP_DATA_CONNECT_TIMEOUT", 10, minimo=1, maximo=300)
FTP_CONTROL_TIMEOUT = _entorno_entero("FTP_CONTROL_TIMEOUT", 300, minimo=1, maximo=3600)
FTP_MAX_LOGIN_ATTEMPTS = _entorno_entero("FTP_MAX_LOGIN_ATTEMPTS", 3, minimo=1, maximo=20)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)


def validar_configuracion_arranque() -> Path:
    """
    Valida credenciales y raíz al arrancar. Crea la raíz si no existe,
    comprueba que es utilizable y la devuelve ya resuelta.
    Nunca cambia permisos ni borra contenido existente.
    """
    if not FTP_USUARIO or not FTP_CLAVE:
        raise SystemExit(
            "No se puede arrancar sin credenciales.\n"
            "Define las variables de entorno FTP_USUARIO y FTP_CLAVE antes de ejecutar:\n"
            "  Windows : set FTP_USUARIO=juan  &&  set FTP_CLAVE=tu_clave\n"
            "  Linux   : export FTP_USUARIO=juan FTP_CLAVE=tu_clave"
        )
    raiz = Path(FTP_ROOT)
    try:
        raiz.mkdir(parents=True, exist_ok=True)
        raiz = raiz.resolve()
        if not raiz.is_dir():
            raise SystemExit(f"La raíz FTP {raiz} no es un directorio")
        # Sonda de escritura: crea y borra SOLO su propio archivo temporal.
        fd, sonda = tempfile.mkstemp(prefix=".ftp-sonda-", dir=str(raiz))
        os.close(fd)
        os.unlink(sonda)
    except SystemExit:
        raise
    except OSError as e:
        raise SystemExit(f"La raíz FTP {FTP_ROOT} no es utilizable: {e}")
    return raiz


# ---------------------------------------------------------------------------
# Lector de canal de control: lectura por bloques con búfer por sesión
# ---------------------------------------------------------------------------


class LectorControl:
    """
    Lee líneas de comandos FTP desde el socket de control.

    - recv() por bloques (no byte a byte).
    - Conserva los bytes sobrantes: si llegan varios comandos juntos o un
      comando fragmentado, se procesan correctamente.
    - Acepta CRLF y LF.
    - Limita cada línea a max_bytes; una línea mayor cierra la sesión
      (violación de protocolo) sin acumulación ilimitada.
    - EOF, timeout y errores de red devuelven None (sin bucles infinitos).
    """

    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._buf = bytearray()

    def leer_linea(self, max_bytes: int) -> str | None:
        while True:
            idx = self._buf.find(b"\n")
            if idx != -1:
                if idx > max_bytes:
                    # Línea demasiado larga: violación de protocolo.
                    del self._buf[: idx + 1]
                    return None
                linea = bytes(self._buf[:idx])
                del self._buf[: idx + 1]
                if linea.endswith(b"\r"):
                    linea = linea[:-1]
                return linea.decode("utf-8", errors="replace")
            if len(self._buf) > max_bytes:
                return None
            try:
                datos = self._sock.recv(4096)
            except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError):
                return None
            if not datos:
                return None
            self._buf.extend(datos)


# ---------------------------------------------------------------------------
# Validación de rutas de filesystem
# ---------------------------------------------------------------------------


def dentro_de_raiz(ruta: Path, raiz: Path) -> bool:
    """
    Indica si 'ruta' (ya resuelta) está contenida en 'raiz'.

    Se usa Path.is_relative_to: compara por componentes. Un startswith
    textual daría falsos positivos (p. ej. raiz=/datos/ftp y
    ruta=/datos/ftp_privado/x).
    """
    try:
        return ruta.is_relative_to(raiz)
    except (OSError, ValueError):
        return False


def resolver_ruta_arg(cwd: Path, raiz: Path, arg: str) -> Path | None:
    """
    Resuelve una ruta FTP (relativa o absoluta) contra la raíz virtual "/".

    - Rutas que empiezan por "/" se resuelven desde la raíz.
    - Los componentes ".." no pueden salir de la raíz (se devuelve None).
    - Se normalizan separadores "\\" a "/".
    - El resultado se resuelve (sigue enlaces simbólicos) y se comprueba
      con dentro_de_raiz. Los enlaces que apunten FUERA de la raíz quedan
      bloqueados; los que apunten dentro se aceptan.
    """
    if arg:
        base = raiz if arg.startswith("/") else cwd
        segmentos = arg.replace("\\", "/").split("/")
    else:
        return cwd
    destino = base
    for s in segmentos:
        if s in ("", "."):
            continue
        if s == "..":
            destino = destino.parent
            continue
        destino = destino / s
    try:
        resuelto = destino.resolve()
    except (OSError, ValueError):
        return None
    if not dentro_de_raiz(resuelto, raiz):
        return None
    return resuelto


def validar_lectura(fpath: Path, raiz: Path) -> bool:
    """Comprueba que 'fpath' es un archivo legible dentro de la raíz."""
    try:
        if not dentro_de_raiz(fpath, raiz):
            return False
        if fpath.is_symlink():
            return False
        return fpath.is_file()
    except OSError:
        return False


def validar_escritura(fpath: Path, raiz: Path) -> bool:
    """
    Comprueba que se puede publicar un archivo en 'fpath' dentro de la raíz.

    Rechaza directorios, enlaces simbólicos existentes y padres fuera de la
    raíz o inexistentes. Es best-effort frente a TOCTOU (ver docstring del
    módulo).
    """
    try:
        if not dentro_de_raiz(fpath, raiz):
            return False
        if fpath.is_symlink():
            return False
        if fpath.exists() and not fpath.is_file():
            return False
        padre = fpath.parent
        if not dentro_de_raiz(padre.resolve(), raiz):
            return False
        if not padre.is_dir() or padre.is_symlink():
            return False
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Utilidades de protocolo
# ---------------------------------------------------------------------------


def enviar_respuesta(conn: socket.socket, codigo: int, mensaje: str) -> None:
    """Envía una línea de respuesta FTP (CRLF)."""
    conn.sendall(f"{codigo} {mensaje}\r\n".encode("utf-8", errors="replace"))


def formato_pasv(ip: str, puerto: int) -> str:
    """Formato PASV: (h1,h2,h3,h4,p1,p2)."""
    partes = ip.split(".")
    if len(partes) != 4:
        partes = ["127", "0", "0", "1"]
    p1, p2 = divmod(puerto, 256)
    return f"({','.join(partes)},{p1},{p2})"


def listar_directorio(ruta: Path) -> bytes:
    """
    Listado LIST estilo Unix, orden determinista (alfabético, sensible a
    mayúsculas). Los nombres con CR/LF se sanear para que no falsifiquen
    registros. Se limitan entradas (10000) y tamaño total (~4 MiB).
    """
    lineas: list[str] = []
    try:
        entradas = sorted(ruta.iterdir(), key=lambda e: e.name)
    except OSError:
        return b""
    total = 0
    for e in entradas:
        if len(lineas) >= 10000 or total >= 4 * 1024 * 1024:
            break
        nombre = e.name.replace("\r", "_").replace("\n", "_")
        try:
            st = e.stat(follow_symlinks=False)
            if e.is_dir():
                linea = f"drwxr-xr-x 1 owner group 0 Jan  1 00:00 {nombre}\r\n"
            else:
                linea = f"-rw-r--r-- 1 owner group {st.st_size} Jan  1 00:00 {nombre}\r\n"
        except OSError:
            continue
        lineas.append(linea)
        total += len(linea)
    return "".join(lineas).encode("utf-8", errors="replace")


def _aceptar_canal_datos(pasv_socket: socket.socket, addr_control) -> socket.socket:
    """
    Acepta la conexión de datos con FTP_DATA_CONNECT_TIMEOUT y comprueba
    que la IP del cliente de datos coincide con la del cliente de control.
    """
    pasv_socket.settimeout(FTP_DATA_CONNECT_TIMEOUT)
    data_conn, data_addr = pasv_socket.accept()
    if data_addr[0] != addr_control[0]:
        data_conn.close()
        raise OSError("la IP del canal de datos no coincide con la del canal de control")
    return data_conn


def _cerrar_socket(sock: socket.socket | None) -> None:
    """Cierra un socket ignorando errores."""
    if sock is not None:
        try:
            sock.close()
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Sesión FTP
# ---------------------------------------------------------------------------


def sesion_ftp(conn: socket.socket, addr, semaforo: threading.BoundedSemaphore,
               raiz: Path) -> None:
    """Maneja una sesión FTP en un hilo. Libera SIEMPRE el semáforo."""
    if not semaforo.acquire(blocking=False):
        try:
            enviar_respuesta(conn, 421, "Demasiadas conexiones, cierre el servicio")
        except OSError:
            pass
        _cerrar_socket(conn)
        logging.warning("Conexión rechazada por límite de clientes desde %s", addr)
        return
    try:
        _sesion_ftp_impl(conn, addr, raiz)
    finally:
        semaforo.release()


def _sesion_ftp_impl(conn: socket.socket, addr, raiz: Path) -> None:
    conn.settimeout(FTP_CONTROL_TIMEOUT)
    lector = LectorControl(conn)
    cwd = raiz
    logged_in = False
    ultimo_usuario: str | None = None
    intentos_fallidos = 0
    pasv_socket: socket.socket | None = None

    def cerrar_pasv() -> None:
        nonlocal pasv_socket
        _cerrar_socket(pasv_socket)
        pasv_socket = None

    try:
        enviar_respuesta(conn, 220, "Servidor FTP listo (sin librerías externas)")
        logging.info("Conexión aceptada desde %s", addr)
        while True:
            linea = lector.leer_linea(FTP_MAX_COMMAND_BYTES)
            if linea is None:
                break
            partes = linea.split(maxsplit=1)
            cmd = (partes[0] if partes else "").upper()
            arg = (partes[1] if len(partes) > 1 else "").strip()

            if cmd == "USER":
                ultimo_usuario = arg
                logged_in = False
                enviar_respuesta(conn, 331, "Usuario OK, contraseña requerida")

            elif cmd == "PASS":
                if ultimo_usuario is None:
                    enviar_respuesta(conn, 503, "Primero envíe USER")
                    continue
                if intentos_fallidos >= FTP_MAX_LOGIN_ATTEMPTS:
                    logging.warning("Cerrando sesión por exceso de intentos desde %s", addr)
                    enviar_respuesta(conn, 530, "Demasiados intentos fallidos")
                    break
                # compare_digest en bytes: mismo tiempo acierte o falle y no
                # revienta con no-ASCII (TypeError en cadenas con acentos).
                usuario_ok = hmac.compare_digest(
                    ultimo_usuario.encode("utf-8"), FTP_USUARIO.encode("utf-8")
                )
                clave_ok = hmac.compare_digest(
                    arg.encode("utf-8"), FTP_CLAVE.encode("utf-8")
                )
                if usuario_ok and clave_ok:
                    logged_in = True
                    logging.info("Login correcto desde %s", addr)
                    enviar_respuesta(conn, 230, "Usuario conectado")
                else:
                    # Mismo mensaje para usuario y clave incorrectos: no se
                    # revela qué credencial falló.
                    logged_in = False
                    ultimo_usuario = None
                    intentos_fallidos += 1
                    enviar_respuesta(conn, 530, "Credenciales incorrectas")

            elif cmd == "SYST":
                enviar_respuesta(conn, 215, "UNIX Type: L8")

            elif cmd == "TYPE":
                if arg.upper() == "I":
                    enviar_respuesta(conn, 200, "Modo binario")
                else:
                    enviar_respuesta(conn, 504, "Solo TYPE I soportado")

            elif cmd == "PWD":
                try:
                    rel = cwd.relative_to(raiz)
                    mostrado = "/" + "/".join(rel.parts) if rel.parts else "/"
                except ValueError:
                    mostrado = "/"
                # Escapar comillas dobles en la ruta mostrada (RFC 959).
                mostrado = mostrado.replace('"', '""')
                enviar_respuesta(conn, 257, f'"{mostrado}" es el directorio actual')

            elif cmd == "CWD":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                nuevo = resolver_ruta_arg(cwd, raiz, arg)
                if nuevo is not None and nuevo.is_dir():
                    cwd = nuevo
                    enviar_respuesta(conn, 250, "Directorio cambiado")
                else:
                    enviar_respuesta(conn, 550, "No se puede cambiar de directorio")

            elif cmd == "PASV":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                cerrar_pasv()
                try:
                    pasv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    pasv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    # Se enlaza a la MISMA interfaz que el canal de control:
                    # el canal de datos nunca está más expuesto que la
                    # autenticación.
                    pasv_socket.bind((FTP_HOST, 0))
                    pasv_socket.listen(1)
                    _, puerto = pasv_socket.getsockname()
                    # La dirección anunciada se deriva de FTP_HOST, coherente
                    # con el bind real.
                    enviar_respuesta(conn, 227, f"Entrando en modo pasivo {formato_pasv(FTP_HOST, puerto)}")
                except OSError:
                    cerrar_pasv()
                    enviar_respuesta(conn, 425, "No se pudo abrir puerto pasivo")

            elif cmd == "LIST":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                if pasv_socket is None:
                    enviar_respuesta(conn, 425, "Use PASV primero")
                    continue
                objetivo = resolver_ruta_arg(cwd, raiz, arg) if arg else cwd
                if objetivo is None or not objetivo.is_dir() or not dentro_de_raiz(objetivo, raiz):
                    cerrar_pasv()
                    enviar_respuesta(conn, 550, "No se puede listar el directorio")
                    continue
                try:
                    contenido = listar_directorio(objetivo)
                except OSError:
                    cerrar_pasv()
                    enviar_respuesta(conn, 550, "No se puede listar el directorio")
                    continue
                try:
                    enviar_respuesta(conn, 150, "Abriendo conexión de datos para LIST")
                    data_conn = _aceptar_canal_datos(pasv_socket, addr)
                    try:
                        data_conn.sendall(contenido)
                    finally:
                        _cerrar_socket(data_conn)
                    enviar_respuesta(conn, 226, "Transferencia completada")
                except (OSError, socket.timeout) as e:
                    # Tras el 150, un fallo NO puede ser 226.
                    logging.warning("Error en LIST desde %s: %s", addr, e)
                    enviar_respuesta(conn, 426, "Conexión de datos fallida")
                finally:
                    cerrar_pasv()

            elif cmd == "RETR":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                if pasv_socket is None:
                    enviar_respuesta(conn, 425, "Use PASV primero")
                    continue
                fpath = resolver_ruta_arg(cwd, raiz, arg)
                if fpath is None or not validar_lectura(fpath, raiz):
                    cerrar_pasv()
                    enviar_respuesta(conn, 550, "Archivo no disponible")
                    continue
                try:
                    enviar_respuesta(conn, 150, "Abriendo conexión de datos para RETR")
                    data_conn = _aceptar_canal_datos(pasv_socket, addr)
                    try:
                        with open(fpath, "rb") as f:
                            while True:
                                trozo = f.read(65536)
                                if not trozo:
                                    break
                                data_conn.sendall(trozo)
                    finally:
                        _cerrar_socket(data_conn)
                    enviar_respuesta(conn, 226, "Transferencia completada")
                except (OSError, socket.timeout) as e:
                    logging.warning("Error en RETR desde %s: %s", addr, e)
                    enviar_respuesta(conn, 426, "Conexión de datos fallida")
                finally:
                    cerrar_pasv()

            elif cmd == "STOR":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                if pasv_socket is None:
                    enviar_respuesta(conn, 425, "Use PASV primero")
                    continue
                fpath = resolver_ruta_arg(cwd, raiz, arg)
                if fpath is None or not validar_escritura(fpath, raiz):
                    cerrar_pasv()
                    enviar_respuesta(conn, 550, "Acceso denegado")
                    continue
                # Publicación segura: se escribe SIEMPRE en un temporal
                # (mkstemp con O_EXCL en el directorio de destino) y solo se
                # publica con os.replace cuando la recepción termina bien.
                # Ante desconexión, exceso de tamaño o error de E/S se borra
                # el temporal y el archivo anterior queda intacto.
                temp_path: str | None = None
                try:
                    enviar_respuesta(conn, 150, "Abriendo conexión de datos para STOR")
                    data_conn = _aceptar_canal_datos(pasv_socket, addr)
                    try:
                        fd, temp_path = tempfile.mkstemp(
                            prefix=".ftp-tmp-", dir=str(fpath.parent)
                        )
                        recibidos = 0
                        with os.fdopen(fd, "wb") as f:
                            while True:
                                trozo = data_conn.recv(65536)
                                if not trozo:
                                    break
                                recibidos += len(trozo)
                                if recibidos > FTP_MAX_UPLOAD_BYTES:
                                    raise OSError(
                                        f"subida excede FTP_MAX_UPLOAD_BYTES={FTP_MAX_UPLOAD_BYTES}"
                                    )
                                f.write(trozo)
                            f.flush()
                            try:
                                os.fsync(f.fileno())
                            except OSError:
                                # fsync puede fallar en FS sin soporte; la
                                # publicación continúa (ver docstring).
                                pass
                    finally:
                        _cerrar_socket(data_conn)
                    # Publicación atómica en el mismo volumen.
                    os.replace(temp_path, str(fpath))
                    temp_path = None
                    enviar_respuesta(conn, 226, "Transferencia completada")
                except (socket.timeout,) as e:
                    logging.warning("Timeout de canal de datos en STOR desde %s: %s", addr, e)
                    enviar_respuesta(conn, 426, "Conexión de datos fallida")
                except OSError as e:
                    if "excede FTP_MAX_UPLOAD_BYTES" in str(e):
                        logging.warning("STOR rechazado por tamaño desde %s", addr)
                        enviar_respuesta(conn, 552, "Archivo excede el tamaño máximo permitido")
                    else:
                        logging.warning("Error en STOR desde %s: %s", addr, e)
                        enviar_respuesta(conn, 450, "No se pudo guardar el archivo")
                finally:
                    if temp_path is not None:
                        try:
                            os.unlink(temp_path)
                        except OSError:
                            pass
                    cerrar_pasv()

            elif cmd == "NOOP":
                enviar_respuesta(conn, 200, "OK")

            elif cmd == "QUIT":
                enviar_respuesta(conn, 221, "Adiós")
                break

            else:
                enviar_respuesta(conn, 502, "Comando no implementado")
    except Exception:
        # Error inesperado: se registra aquí, jamás se filtra al cliente.
        logging.exception("Error inesperado en sesión desde %s", addr)
    finally:
        cerrar_pasv()
        _cerrar_socket(conn)
        logging.info("Sesión desde %s finalizada", addr)


# ---------------------------------------------------------------------------
# Arranque del servidor
# ---------------------------------------------------------------------------


def crear_socket_escucha() -> socket.socket:
    """Crea, enlaza y escucha el socket de control."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((FTP_HOST, FTP_PORT))
    except OSError as e:
        _cerrar_socket(sock)
        raise SystemExit(f"No se puede enlazar a {FTP_HOST}:{FTP_PORT}: {e}")
    sock.listen(50)
    return sock


def bucle_aceptar(sock: socket.socket, raiz: Path,
                  detener: threading.Event | None = None) -> None:
    """
    Bucle de aceptación. Usa un timeout corto en accept() para poder
    apagar el servidor sin bloquearse (KeyboardInterrupt o evento detener).
    Cierra el socket de escucha al salir.
    """
    semaforo = threading.BoundedSemaphore(FTP_MAX_CLIENTS)
    sock.settimeout(0.5)
    try:
        while detener is None or not detener.is_set():
            try:
                conn, addr = sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(
                target=sesion_ftp, args=(conn, addr, semaforo, raiz), daemon=True
            ).start()
    finally:
        _cerrar_socket(sock)
        logging.info("Servidor detenido")


def main() -> None:
    raiz = validar_configuracion_arranque()
    sock = crear_socket_escucha()
    puerto_real = sock.getsockname()[1]
    logging.info("Servidor FTP escuchando en %s:%s", FTP_HOST, puerto_real)
    logging.info("Raíz FTP: %s", raiz)
    logging.info(
        "Límites: max_clients=%s max_upload=%s max_cmd=%s data_timeout=%ss control_timeout=%ss",
        FTP_MAX_CLIENTS, FTP_MAX_UPLOAD_BYTES, FTP_MAX_COMMAND_BYTES,
        FTP_DATA_CONNECT_TIMEOUT, FTP_CONTROL_TIMEOUT,
    )
    try:
        bucle_aceptar(sock, raiz)
    except KeyboardInterrupt:
        logging.info("Interrupción recibida, apagando…")
        _cerrar_socket(sock)


if __name__ == "__main__":
    main()

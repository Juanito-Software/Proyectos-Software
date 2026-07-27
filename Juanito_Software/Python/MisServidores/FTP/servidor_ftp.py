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
Solo biblioteca estándar: socket, threading, os, pathlib. Sin librerías FTP.
"""

import hmac
import os
import socket
import threading
from pathlib import Path

# Configuración
#
# HOST es 127.0.0.1 y no "0.0.0.0" a proposito. Escuchar en todas las
# interfaces expondria a toda la red local un servidor de ficheros con permiso
# de lectura y escritura. Ademas seria incoherente con el propio codigo: el
# modo pasivo anuncia al cliente la direccion 127.0.0.1 como destino del canal
# de datos, de modo que las transferencias solo funcionan cuando el cliente
# esta en esta misma maquina. Este servidor ya era local; ahora tambien lo dice
# su configuracion.
HOST = "127.0.0.1"
PUERTO = 2121
RAIZ_FTP = Path(__file__).resolve().parent  # directorio del script como raíz FTP

# Credenciales de acceso. Se leen del entorno para no versionarlas:
#
#   set FTP_USUARIO=juan
#   set FTP_CLAVE=loquesea
#
# Si faltan, el servidor no arranca. Es deliberado: arrancar sin credenciales
# significaria aceptar a cualquiera, que es exactamente lo que hacia antes.
USUARIO_FTP = os.environ.get("FTP_USUARIO", "")
CLAVE_FTP = os.environ.get("FTP_CLAVE", "")


def dentro_de_raiz(ruta: Path, raiz: Path) -> bool:
    """
    Indica si 'ruta' esta contenida en 'raiz'.

    Se usa Path.is_relative_to en lugar de comparar cadenas con startswith.
    La comparacion textual es un error clasico: si la raiz es /datos/FTP, la
    ruta /datos/FTP_privado tambien empieza por esa cadena y pasaria el filtro
    pese a estar fuera. is_relative_to compara por componentes de ruta y no
    tiene ese problema.
    """
    try:
        return ruta.resolve().is_relative_to(raiz)
    except (OSError, ValueError):
        return False


def enviar_respuesta(conn: socket.socket, codigo: int, mensaje: str) -> None:
    """Envía una línea de respuesta FTP (CRLF)."""
    conn.sendall(f"{codigo} {mensaje}\r\n".encode("utf-8", errors="replace"))


def leer_linea(conn: socket.socket) -> str | None:
    """Lee una línea del socket de control (hasta CRLF o LF)."""
    buf = b""
    while True:
        try:
            b = conn.recv(1)
        except (ConnectionResetError, BrokenPipeError):
            return None
        if not b:
            return None
        buf += b
        if buf.endswith(b"\r\n") or buf.endswith(b"\n"):
            break
    return buf.decode("utf-8", errors="replace").strip().replace("\r", "").replace("\n", "")


def formato_pasv(ip: str, puerto: int) -> str:
    """Formato PASV: (h1,h2,h3,h4,p1,p2)."""
    partes = ip.replace(".", ",").split(",")
    if len(partes) != 4:
        partes = ["127", "0", "0", "1"]
    p1, p2 = puerto // 256, puerto % 256
    return f"({','.join(partes)},{p1},{p2})"


def listar_directorio(ruta: Path) -> bytes:
    """Genera listado tipo LIST (estilo Unix)."""
    lineas = []
    try:
        for e in sorted(ruta.iterdir(), key=lambda x: x.name.lower()):
            try:
                st = e.stat()
                if e.is_dir():
                    lineas.append(f"drwxr-xr-x 1 owner group 0 Jan 1 00:00 {e.name}\r\n")
                else:
                    lineas.append(f"-rw-r--r-- 1 owner group {st.st_size} Jan 1 00:00 {e.name}\r\n")
            except OSError:
                continue
    except OSError:
        pass
    return "".join(lineas).encode("utf-8", errors="replace")


def sesion_ftp(conn: socket.socket, cliente_addr) -> None:
    """Maneja una sesión FTP en un hilo."""
    conn.settimeout(300)
    enviar_respuesta(conn, 220, "Servidor FTP listo (sin librerías externas)")

    root = RAIZ_FTP.resolve()
    cwd = root
    logged_in = False
    last_user: str | None = None
    pasv_socket: socket.socket | None = None

    try:
        while True:
            linea = leer_linea(conn)
            if linea is None:
                break

            partes = linea.split(maxsplit=1)
            cmd = (partes[0] if partes else "").upper()
            arg = (partes[1] if len(partes) > 1 else "").strip()

            if cmd == "USER":
                last_user = arg
                enviar_respuesta(conn, 331, "Usuario OK, contraseña requerida")

            elif cmd == "PASS":
                if last_user is None:
                    enviar_respuesta(conn, 503, "Primero envíe USER")
                    continue
                # Se comparan usuario y clave con compare_digest, que tarda lo
                # mismo acierte o falle. Un '==' normal corta en el primer
                # caracter distinto, y ese tiempo desigual permite adivinar la
                # clave caracter a caracter midiendo la respuesta.
                #
                # Se compara en bytes y no en texto: compare_digest solo acepta
                # cadenas de texto ASCII, asi que un usuario con acentos o 'ñ'
                # lanzaria TypeError y dejaria la conexion colgada sin responder.
                usuario_ok = hmac.compare_digest(
                    last_user.encode("utf-8"), USUARIO_FTP.encode("utf-8")
                )
                clave_ok = hmac.compare_digest(
                    arg.encode("utf-8"), CLAVE_FTP.encode("utf-8")
                )
                if usuario_ok and clave_ok:
                    logged_in = True
                    enviar_respuesta(conn, 230, "Usuario conectado")
                else:
                    # Mismo mensaje para usuario inexistente y clave incorrecta:
                    # distinguirlos revelaria que usuarios existen.
                    logged_in = False
                    last_user = None
                    enviar_respuesta(conn, 530, "Credenciales incorrectas")

            elif cmd == "SYST":
                enviar_respuesta(conn, 215, "UNIX Type: L8")

            elif cmd == "PWD":
                try:
                    rel = cwd.relative_to(root)
                    shown = "/" + "/".join(rel.parts) if rel.parts else "/"
                except ValueError:
                    shown = "/"
                enviar_respuesta(conn, 257, f'"{shown}" es el directorio actual')

            elif cmd == "CWD":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                if arg.startswith("/"):
                    base = root
                    segs = arg.strip("/").replace("\\", "/").split("/")
                else:
                    base = cwd
                    segs = arg.replace("\\", "/").split("/")
                nuevo = base
                for s in segs:
                    if s in ("", "."):
                        continue
                    if s == "..":
                        nuevo = nuevo.parent
                        continue
                    nuevo = nuevo / s
                try:
                    nuevo = nuevo.resolve()
                    if nuevo.is_dir() and dentro_de_raiz(nuevo, root):
                        cwd = nuevo
                        enviar_respuesta(conn, 250, "Directorio cambiado")
                    else:
                        enviar_respuesta(conn, 550, "No se puede cambiar de directorio")
                except OSError:
                    enviar_respuesta(conn, 550, "No se puede cambiar de directorio")

            elif cmd == "TYPE":
                if arg.upper() == "I":
                    enviar_respuesta(conn, 200, "Modo binario")
                else:
                    enviar_respuesta(conn, 504, "Solo TYPE I soportado")

            elif cmd == "PASV":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                if pasv_socket:
                    try:
                        pasv_socket.close()
                    except OSError:
                        pass
                try:
                    pasv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    pasv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    # Se enlaza al mismo HOST que el socket de control, no a
                    # "0.0.0.0": el canal de datos no debe estar mas expuesto
                    # que el canal por el que se autentica el cliente.
                    pasv_socket.bind((HOST, 0))
                    pasv_socket.listen(1)
                    _, puerto = pasv_socket.getsockname()
                    # La direccion que se anuncia se deriva de HOST, no de un
                    # literal. Antes estaba escrita a mano y podia dejar de
                    # coincidir con la interfaz donde realmente se escucha, que
                    # es como el servidor acababa anunciando una direccion
                    # inalcanzable para el cliente.
                    pasv_str = formato_pasv(HOST, puerto)
                    enviar_respuesta(conn, 227, f"Entrando en modo pasivo {pasv_str}")
                except OSError:
                    enviar_respuesta(conn, 425, "No se pudo abrir puerto pasivo")

            elif cmd == "LIST":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                if not pasv_socket:
                    enviar_respuesta(conn, 425, "Use PASV primero")
                    continue
                enviar_respuesta(conn, 150, "Abriendo conexión de datos para LIST")
                try:
                    data_conn, _ = pasv_socket.accept()
                    dir_listar = (cwd / arg) if arg else cwd
                    if dir_listar.is_dir() and dentro_de_raiz(dir_listar, root):
                        data_conn.sendall(listar_directorio(dir_listar))
                    data_conn.close()
                    enviar_respuesta(conn, 226, "Transferencia completada")
                except (OSError, socket.timeout):
                    enviar_respuesta(conn, 550, "Error en LIST")
                finally:
                    try:
                        pasv_socket.close()
                    except OSError:
                        pass
                    pasv_socket = None

            elif cmd == "RETR":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                if not pasv_socket:
                    enviar_respuesta(conn, 425, "Use PASV primero")
                    continue
                fpath = (cwd / arg).resolve()
                if not fpath.is_file() or not dentro_de_raiz(fpath, root):
                    enviar_respuesta(conn, 550, "Archivo no existe")
                    continue
                enviar_respuesta(conn, 150, "Abriendo conexión de datos para RETR")
                try:
                    data_conn, _ = pasv_socket.accept()
                    with open(fpath, "rb") as f:
                        while True:
                            chunk = f.read(65536)
                            if not chunk:
                                break
                            data_conn.sendall(chunk)
                    data_conn.close()
                    enviar_respuesta(conn, 226, "Transferencia completada")
                except (OSError, socket.timeout):
                    enviar_respuesta(conn, 550, "Error en RETR")
                finally:
                    try:
                        pasv_socket.close()
                    except OSError:
                        pass
                    pasv_socket = None

            elif cmd == "STOR":
                if not logged_in:
                    enviar_respuesta(conn, 530, "No conectado")
                    continue
                if not pasv_socket:
                    enviar_respuesta(conn, 425, "Use PASV primero")
                    continue
                fpath = (cwd / arg).resolve()
                if not dentro_de_raiz(fpath, root):
                    enviar_respuesta(conn, 550, "Acceso denegado")
                    continue
                enviar_respuesta(conn, 150, "Abriendo conexión de datos para STOR")
                try:
                    data_conn, _ = pasv_socket.accept()
                    with open(fpath, "wb") as f:
                        while True:
                            chunk = data_conn.recv(65536)
                            if not chunk:
                                break
                            f.write(chunk)
                    data_conn.close()
                    enviar_respuesta(conn, 226, "Transferencia completada")
                except (OSError, socket.timeout):
                    enviar_respuesta(conn, 550, "Error en STOR")
                finally:
                    try:
                        pasv_socket.close()
                    except OSError:
                        pass
                    pasv_socket = None

            elif cmd == "NOOP":
                enviar_respuesta(conn, 200, "OK")

            elif cmd == "QUIT":
                enviar_respuesta(conn, 221, "Adiós")
                break

            else:
                enviar_respuesta(conn, 502, "Comando no implementado")
    finally:
        if pasv_socket:
            try:
                pasv_socket.close()
            except OSError:
                pass
        try:
            conn.close()
        except OSError:
            pass


def main() -> None:
    if not USUARIO_FTP or not CLAVE_FTP:
        raise SystemExit(
            "No se puede arrancar sin credenciales.\n"
            "Define las variables de entorno FTP_USUARIO y FTP_CLAVE antes de ejecutar:\n"
            "  Windows : set FTP_USUARIO=juan  &&  set FTP_CLAVE=tu_clave\n"
            "  Linux   : export FTP_USUARIO=juan FTP_CLAVE=tu_clave"
        )

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PUERTO))
    servidor.listen(50)
    print(f"Servidor FTP escuchando en {HOST}:{PUERTO}")
    print(f"Raíz FTP: {RAIZ_FTP}")

    while True:
        try:
            conn, addr = servidor.accept()
            threading.Thread(target=sesion_ftp, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            break
        except OSError as e:
            print(f"Error aceptando: {e}")

    servidor.close()


if __name__ == "__main__":
    main()

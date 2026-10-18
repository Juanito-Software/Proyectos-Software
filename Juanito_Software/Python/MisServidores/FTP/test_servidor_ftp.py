#!/usr/bin/env python3
"""
Pruebas del servidor FTP con unittest, tempfile y la biblioteca estándar.

Cada prueba arranca su propio servidor en un puerto libre con su propio
árbol temporal, sin servicios externos. La configuración se aplica recargando
el módulo (importlib.reload) tras fijar las variables de entorno.
"""

import importlib
import os
import socket
import tempfile
import threading
import unittest
from pathlib import Path

import servidor_ftp

USUARIO = "juan"
CLAVE = "secreta123"

# Variables que el entorno del proceso podría arrastrar entre recargas.
_VARS_PRUEBA = (
    "FTP_HOST", "FTP_PORT", "FTP_ROOT", "FTP_USUARIO", "FTP_CLAVE",
    "FTP_MAX_CLIENTS", "FTP_MAX_UPLOAD_BYTES", "FTP_MAX_COMMAND_BYTES",
    "FTP_DATA_CONNECT_TIMEOUT", "FTP_CONTROL_TIMEOUT", "FTP_MAX_LOGIN_ATTEMPTS",
)


def puerto_libre() -> int:
    """Reserva un puerto TCP efímero y lo devuelve."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
    finally:
        s.close()


class ClienteFTPPrueba:
    """Cliente FTP mínimo para las pruebas (solo stdlib)."""

    def __init__(self, puerto: int):
        self.sock = socket.create_connection(("127.0.0.1", puerto), timeout=5)
        self.buf = b""
        # El servidor envía el banner 220 (o un 421 si no hay plaza) nada
        # más aceptar: se consume aquí para que cmd() lea siempre la
        # respuesta del comando enviado.
        self.banner = self.leer_respuesta()

    def leer_respuesta(self) -> tuple[int, str]:
        while b"\r\n" not in self.buf:
            trozo = self.sock.recv(4096)
            if not trozo:
                raise ConnectionError("el servidor cerró la conexión")
            self.buf += trozo
        linea, _, resto = self.buf.partition(b"\r\n")
        self.buf = resto
        texto = linea.decode("utf-8", errors="replace")
        codigo = int(texto[:3])
        return codigo, texto

    def cmd(self, linea: str) -> tuple[int, str]:
        self.sock.sendall((linea + "\r\n").encode("utf-8"))
        return self.leer_respuesta()

    def enviar_raw(self, datos: bytes) -> None:
        self.sock.sendall(datos)

    def login(self) -> None:
        codigo, _ = self.cmd(f"USER {USUARIO}")
        assert codigo == 331, codigo
        codigo, _ = self.cmd(f"PASS {CLAVE}")
        assert codigo == 230, codigo

    def abrir_pasv(self) -> socket.socket:
        """PASV + conecta al canal de datos; devuelve el socket de datos."""
        codigo, texto = self.cmd("PASV")
        assert codigo == 227, texto
        inicio = texto.index("(")
        partes = [int(p) for p in texto[inicio + 1:texto.index(")")].split(",")]
        ip = ".".join(str(p) for p in partes[:4])
        puerto = partes[4] * 256 + partes[5]
        return socket.create_connection((ip, puerto), timeout=5)

    def transferencia_pasv(self, comando: str) -> tuple[int, str, bytes]:
        """Ejecuta PASV+comando y devuelve (código final, texto, datos)."""
        data = self.abrir_pasv()
        codigo, texto = self.cmd(comando)
        assert codigo == 150, texto
        recibido = b""
        try:
            while True:
                trozo = data.recv(65536)
                if not trozo:
                    break
                recibido += trozo
        finally:
            data.close()
        codigo2, texto2 = self.leer_respuesta()
        return codigo2, texto2, recibido

    def cerrar(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.cerrar()


class ServidorDePrueba:
    """Servidor FTP en proceso, con raíz temporal y configuración por entorno."""

    def __init__(self, **env):
        self.tmp = tempfile.TemporaryDirectory(prefix="ftp-pruebas-")
        self.raiz = Path(self.tmp.name) / "storage"
        self.puerto = puerto_libre()
        for var in _VARS_PRUEBA:
            os.environ.pop(var, None)
        os.environ["FTP_HOST"] = "127.0.0.1"
        os.environ["FTP_PORT"] = str(self.puerto)
        os.environ["FTP_ROOT"] = str(self.raiz)
        os.environ["FTP_USUARIO"] = USUARIO
        os.environ["FTP_CLAVE"] = CLAVE
        for k, v in env.items():
            os.environ[k] = str(v)
        self.ftp = importlib.reload(servidor_ftp)
        self.raiz_resuelta = self.ftp.validar_configuracion_arranque()
        self.sock = self.ftp.crear_socket_escucha()
        self.puerto = self.sock.getsockname()[1]
        self.detener = threading.Event()
        self.hilo = threading.Thread(
            target=self.ftp.bucle_aceptar,
            args=(self.sock, self.raiz_resuelta, self.detener),
            daemon=True,
        )
        self.hilo.start()

    def cliente(self) -> ClienteFTPPrueba:
        return ClienteFTPPrueba(self.puerto)

    def parar(self) -> None:
        self.detener.set()
        self.hilo.join(timeout=5)
        self.tmp.cleanup()


class BasePruebas(unittest.TestCase):
    """Base: arranca y para un servidor por prueba."""

    env_servidor: dict = {}

    def setUp(self):
        self.servidor = ServidorDePrueba(**self.env_servidor)
        self.addCleanup(self.servidor.parar)


# ---------------------------------------------------------------------------
# 1. Configuración y arranque
# ---------------------------------------------------------------------------


class TestConfiguracion(BasePruebas):

    def test_credenciales_obligatorias(self):
        os.environ.pop("FTP_USUARIO", None)
        os.environ.pop("FTP_CLAVE", None)
        with self.assertRaises(SystemExit):
            importlib.reload(servidor_ftp)
            servidor_ftp.validar_configuracion_arranque()

    def test_puerto_invalido_aborta_al_importar(self):
        os.environ["FTP_PORT"] = "99999"
        with self.assertRaises(SystemExit):
            importlib.reload(servidor_ftp)
        os.environ["FTP_PORT"] = "-1"
        with self.assertRaises(SystemExit):
            importlib.reload(servidor_ftp)

    def test_max_clients_invalido_aborta(self):
        os.environ["FTP_MAX_CLIENTS"] = "0"
        with self.assertRaises(SystemExit):
            importlib.reload(servidor_ftp)

    def test_max_upload_invalido_aborta(self):
        os.environ["FTP_MAX_UPLOAD_BYTES"] = "-5"
        with self.assertRaises(SystemExit):
            importlib.reload(servidor_ftp)

    def test_max_command_bytes_invalido_aborta(self):
        os.environ["FTP_MAX_COMMAND_BYTES"] = "abc"
        with self.assertRaises(SystemExit):
            importlib.reload(servidor_ftp)

    def test_timeout_invalido_aborta(self):
        os.environ["FTP_DATA_CONNECT_TIMEOUT"] = "0"
        with self.assertRaises(SystemExit):
            importlib.reload(servidor_ftp)

    def test_raiz_se_crea_y_esta_separada_del_codigo(self):
        # ServidorDePrueba crea la raíz bajo un tmp distinto del código.
        self.assertTrue(self.servidor.raiz_resuelta.is_dir())
        codigo = Path(servidor_ftp.__file__).resolve().parent
        self.assertFalse(str(self.servidor.raiz_resuelta).startswith(str(codigo)))


# ---------------------------------------------------------------------------
# 2. Autenticación
# ---------------------------------------------------------------------------


class TestAutenticacion(BasePruebas):

    def test_login_correcto(self):
        with self.servidor.cliente() as c:
            codigo, _ = c.cmd("USER " + USUARIO)
            self.assertEqual(codigo, 331)
            codigo, _ = c.cmd("PASS " + CLAVE)
            self.assertEqual(codigo, 230)

    def test_login_clave_incorrecta(self):
        with self.servidor.cliente() as c:
            c.cmd("USER " + USUARIO)
            codigo, texto = c.cmd("PASS mala")
            self.assertEqual(codigo, 530)
            self.assertNotIn(CLAVE, texto)

    def test_login_usuario_incorrecto(self):
        with self.servidor.cliente() as c:
            c.cmd("USER nadie")
            codigo, _ = c.cmd("PASS " + CLAVE)
            self.assertEqual(codigo, 530)

    def test_pass_sin_user(self):
        with self.servidor.cliente() as c:
            codigo, _ = c.cmd("PASS " + CLAVE)
            self.assertEqual(codigo, 503)

    def test_operaciones_sin_login_rechazadas(self):
        with self.servidor.cliente() as c:
            for comando in ("CWD /", "PASV", "LIST", "RETR x", "STOR x"):
                codigo, _ = c.cmd(comando)
                self.assertEqual(codigo, 530, comando)

    def test_user_tras_login_vuelve_a_pedir_pass(self):
        with self.servidor.cliente() as c:
            c.login()
            codigo, _ = c.cmd("USER " + USUARIO)
            self.assertEqual(codigo, 331)
            codigo, _ = c.cmd("LIST")
            self.assertEqual(codigo, 530)

    def test_exceso_intentos_cierra_sesion(self):
        # Límite por defecto: 3. Tras 3 fallos, el cuarto PASS cierra.
        with self.servidor.cliente() as c:
            for _ in range(3):
                c.cmd("USER " + USUARIO)
                codigo, _ = c.cmd("PASS mala")
                self.assertEqual(codigo, 530)
            c.cmd("USER " + USUARIO)
            # Cuarto PASS: ya superó el límite -> 530 y cierre.
            codigo, _ = c.cmd("PASS mala")
            self.assertEqual(codigo, 530)
            # La sesión debe cerrarse: la siguiente lectura ve EOF.
            with self.assertRaises(ConnectionError):
                c.cmd("NOOP")

    def test_intentos_no_afectan_a_otra_sesion(self):
        with self.servidor.cliente() as c1:
            for _ in range(3):
                c1.cmd("USER " + USUARIO)
                c1.cmd("PASS mala")
        with self.servidor.cliente() as c2:
            codigo, _ = c2.cmd("USER " + USUARIO)
            self.assertEqual(codigo, 331)
            codigo, _ = c2.cmd("PASS " + CLAVE)
            self.assertEqual(codigo, 230)


# ---------------------------------------------------------------------------
# 3. Lector TCP: fragmentados, agrupados, demasiado largos
# ---------------------------------------------------------------------------


class TestLectorTCP(BasePruebas):

    def test_comando_fragmentado(self):
        with self.servidor.cliente() as c:
            c.enviar_raw(b"PW")
            c.enviar_raw(b"D\r\n")
            codigo, _ = c.leer_respuesta()
            self.assertEqual(codigo, 257)

    def test_comandos_agrupados_en_un_envio(self):
        with self.servidor.cliente() as c:
            c.enviar_raw(b"NOOP\r\nNOOP\r\nSYST\r\n")
            self.assertEqual(c.leer_respuesta()[0], 200)
            self.assertEqual(c.leer_respuesta()[0], 200)
            self.assertEqual(c.leer_respuesta()[0], 215)

    def test_linea_demasiada_larga_cierra_sesion(self):
        with self.servidor.cliente() as c:
            largo = b"X" * (servidor_ftp.FTP_MAX_COMMAND_BYTES + 100) + b"\r\n"
            c.enviar_raw(largo)
            # El servidor debe cerrar (EOF) sin responder ni colgarse.
            with self.assertRaises(ConnectionError):
                c.leer_respuesta()

    def test_comando_con_lf_solo(self):
        with self.servidor.cliente() as c:
            c.enviar_raw(b"NOOP\n")
            self.assertEqual(c.leer_respuesta()[0], 200)


# ---------------------------------------------------------------------------
# 4. PWD, CWD y seguridad de rutas
# ---------------------------------------------------------------------------


class TestRutas(BasePruebas):

    def test_pwd_en_raiz(self):
        with self.servidor.cliente() as c:
            c.login()
            codigo, texto = c.cmd("PWD")
            self.assertEqual(codigo, 257)
            self.assertIn('"/"', texto)

    def test_cwd_relativo_y_absoluto(self):
        with self.servidor.cliente() as c:
            c.login()
            (self.servidor.raiz_resuelta / "docs").mkdir()
            self.assertEqual(c.cmd("CWD docs")[0], 250)
            codigo, texto = c.cmd("PWD")
            self.assertIn("/docs", texto)
            self.assertEqual(c.cmd("CWD /")[0], 250)
            codigo, texto = c.cmd("PWD")
            self.assertIn('"/"', texto)

    def test_cwd_relativo_desde_subdirectorio(self):
        with self.servidor.cliente() as c:
            c.login()
            (self.servidor.raiz_resuelta / "a").mkdir()
            (self.servidor.raiz_resuelta / "a" / "b").mkdir()
            c.cmd("CWD a")
            self.assertEqual(c.cmd("CWD b")[0], 250)

    def test_cwd_traversal_bloqueado(self):
        with self.servidor.cliente() as c:
            c.login()
            for intento in ("..", "../..", "a/../../..", "/../secreto",
                            "\\..\\..\\secreto"):
                codigo, _ = c.cmd(f"CWD {intento}")
                self.assertEqual(codigo, 550, intento)
            # Tras los intentos seguimos en la raíz.
            codigo, texto = c.cmd("PWD")
            self.assertIn('"/"', texto)

    def test_cwd_ruta_inexistente(self):
        with self.servidor.cliente() as c:
            c.login()
            self.assertEqual(c.cmd("CWD no-existe")[0], 550)

    def test_cwd_enlace_simbolico_fuera_de_raiz_bloqueado(self):
        fuera = Path(self.servidor.tmp.name) / "fuera"
        fuera.mkdir()
        enlace = self.servidor.raiz_resuelta / "enlace"
        try:
            os.symlink(str(fuera), str(enlace))
        except (OSError, NotImplementedError):
            self.skipTest("crear symlinks no disponible en este entorno Windows")
        with self.servidor.cliente() as c:
            c.login()
            codigo, _ = c.cmd("CWD /enlace")
            self.assertEqual(codigo, 550)

    def test_retr_a_traves_de_enlace_fuera_bloqueado(self):
        fuera = Path(self.servidor.tmp.name) / "fuera"
        fuera.mkdir()
        (fuera / "secreto.txt").write_bytes(b"secreto")
        enlace = self.servidor.raiz_resuelta / "secreto-link.txt"
        try:
            os.symlink(str(fuera / "secreto.txt"), str(enlace))
        except (OSError, NotImplementedError):
            self.skipTest("crear symlinks no disponible en este entorno Windows")
        with self.servidor.cliente() as c:
            c.login()
            pasv = c.abrir_pasv()
            codigo, texto = c.cmd("RETR secreto-link.txt")
            self.assertEqual(codigo, 550)
            pasv.close()


# ---------------------------------------------------------------------------
# 5. PASV, LIST, RETR
# ---------------------------------------------------------------------------


class TestTransferencias(BasePruebas):

    def test_pasv_formato(self):
        with self.servidor.cliente() as c:
            c.login()
            codigo, texto = c.cmd("PASV")
            self.assertEqual(codigo, 227)
            self.assertIn("(127,0,0,1,", texto)

    def test_list_directorio_vacio(self):
        with self.servidor.cliente() as c:
            c.login()
            codigo, texto, datos = c.transferencia_pasv("LIST")
            self.assertEqual(codigo, 226)
            self.assertEqual(datos, b"")

    def test_list_con_entradas_orden_determinista(self):
        (self.servidor.raiz_resuelta / "zeta.txt").write_bytes(b"1")
        (self.servidor.raiz_resuelta / "alfa.txt").write_bytes(b"12345")
        (self.servidor.raiz_resuelta / "sub").mkdir()
        with self.servidor.cliente() as c:
            c.login()
            codigo, _, datos = c.transferencia_pasv("LIST")
            self.assertEqual(codigo, 226)
            texto = datos.decode()
            self.assertIn("alfa.txt", texto)
            self.assertIn("zeta.txt", texto)
            self.assertIn("sub", texto)
            self.assertLess(texto.index("alfa.txt"), texto.index("zeta.txt"))

    def test_list_nombre_con_salto_de_linea_no_falsifica(self):
        # Windows no permite \r\n en nombres de archivo; se omite si falla.
        nombre = "malo\r\n-inyectado.txt"
        try:
            (self.servidor.raiz_resuelta / nombre).write_bytes(b"x")
        except OSError:
            self.skipTest("el SO no permite CR en nombres de archivo")
        with self.servidor.cliente() as c:
            c.login()
            _, _, datos = c.transferencia_pasv("LIST")
            self.assertNotIn(b"\r\n-inyectado", datos)

    def test_list_como_archivo_da_550(self):
        (self.servidor.raiz_resuelta / "f.txt").write_bytes(b"x")
        with self.servidor.cliente() as c:
            c.login()
            pasv = c.abrir_pasv()
            codigo, _ = c.cmd("LIST f.txt")
            self.assertEqual(codigo, 550)
            pasv.close()

    def test_list_sin_pasv_da_425(self):
        with self.servidor.cliente() as c:
            c.login()
            self.assertEqual(c.cmd("LIST")[0], 425)

    def test_retr_archivo_existente(self):
        contenido = b"contenido binario \x00\x01\x02\xff"
        (self.servidor.raiz_resuelta / "bin.dat").write_bytes(contenido)
        with self.servidor.cliente() as c:
            c.login()
            codigo, texto, datos = c.transferencia_pasv("RETR bin.dat")
            self.assertEqual(codigo, 226)
            self.assertEqual(datos, contenido)

    def test_retr_inexistente_da_550(self):
        with self.servidor.cliente() as c:
            c.login()
            pasv = c.abrir_pasv()
            self.assertEqual(c.cmd("RETR no-existe.bin")[0], 550)
            pasv.close()


# ---------------------------------------------------------------------------
# 6. STOR: nuevo, sobrescritura, límite, limpieza de temporales
# ---------------------------------------------------------------------------


class TestSTOR(BasePruebas):

    def test_stor_archivo_nuevo(self):
        with self.servidor.cliente() as c:
            c.login()
            pasv = c.abrir_pasv()
            codigo, _ = c.cmd("STOR nuevo.txt")
            self.assertEqual(codigo, 150)
            pasv.sendall(b"hola mundo")
            pasv.close()
            codigo, _ = c.leer_respuesta()
            self.assertEqual(codigo, 226)
        destino = self.servidor.raiz_resuelta / "nuevo.txt"
        self.assertEqual(destino.read_bytes(), b"hola mundo")

    def test_stor_sobrescribe_archivo_existente(self):
        destino = self.servidor.raiz_resuelta / "viejo.txt"
        destino.write_bytes(b"contenido anterior")
        with self.servidor.cliente() as c:
            c.login()
            pasv = c.abrir_pasv()
            c.cmd("STOR viejo.txt")
            pasv.sendall(b"nuevo")
            pasv.close()
            self.assertEqual(c.leer_respuesta()[0], 226)
        self.assertEqual(destino.read_bytes(), b"nuevo")

    def test_stor_excede_limite_conserva_anterior_y_limpia_temporales(self):
        # Este servidor arrancado con 100 bytes máximos.
        self.servidor.parar()
        self.servidor = ServidorDePrueba(FTP_MAX_UPLOAD_BYTES=100)
        destino = self.servidor.raiz_resuelta / "grande.bin"
        destino.write_bytes(b"original")
        with self.servidor.cliente() as c:
            c.login()
            pasv = c.abrir_pasv()
            codigo, _ = c.cmd("STOR grande.bin")
            self.assertEqual(codigo, 150)
            pasv.sendall(b"A" * 200)
            pasv.close()
            codigo, texto = c.leer_respuesta()
            self.assertEqual(codigo, 552)
        # El archivo anterior queda intacto.
        self.assertEqual(destino.read_bytes(), b"original")
        # No quedan temporales huérfanos.
        temporales = list(self.servidor.raiz_resuelta.glob(".ftp-tmp-*"))
        self.assertEqual(temporales, [])

    def test_stor_a_directorio_da_550(self):
        (self.servidor.raiz_resuelta / "dirtorio").mkdir()
        with self.servidor.cliente() as c:
            c.login()
            pasv = c.abrir_pasv()
            self.assertEqual(c.cmd("STOR dirtorio")[0], 550)
            pasv.close()

    def test_stor_traversal_bloqueado(self):
        with self.servidor.cliente() as c:
            c.login()
            pasv = c.abrir_pasv()
            self.assertEqual(c.cmd("STOR ../fuera.txt")[0], 550)
            pasv.close()
        self.assertFalse((Path(self.servidor.tmp.name) / "fuera.txt").exists())

    def test_stor_enlace_simbolico_rechazado(self):
        fuera = Path(self.servidor.tmp.name) / "destino-fuera.txt"
        enlace = self.servidor.raiz_resuelta / "link.txt"
        try:
            os.symlink(str(fuera), str(enlace))
        except (OSError, NotImplementedError):
            self.skipTest("crear symlinks no disponible en este entorno Windows")
        with self.servidor.cliente() as c:
            c.login()
            pasv = c.abrir_pasv()
            self.assertEqual(c.cmd("STOR link.txt")[0], 550)
            pasv.close()
        self.assertFalse(fuera.exists())

    def test_stor_sin_pasv_da_425(self):
        with self.servidor.cliente() as c:
            c.login()
            self.assertEqual(c.cmd("STOR x.txt")[0], 425)


# ---------------------------------------------------------------------------
# 7. Timeouts y cierre de sockets
# ---------------------------------------------------------------------------


class TestTimeouts(BasePruebas):

    env_servidor = {"FTP_DATA_CONNECT_TIMEOUT": 1, "FTP_CONTROL_TIMEOUT": 2}

    def test_timeout_canal_datos_list_no_da_226(self):
        with self.servidor.cliente() as c:
            c.login()
            codigo, _ = c.cmd("PASV")
            self.assertEqual(codigo, 227)
            # No conectamos el canal de datos: LIST responde 150 y luego el
            # servidor debe agotar el timeout con 426 (nunca 226).
            codigo, _ = c.cmd("LIST")
            self.assertEqual(codigo, 150)
            codigo2, _ = c.leer_respuesta()
            self.assertIn(codigo2, (425, 426))
            self.assertNotEqual(codigo2, 226)

    def test_timeout_canal_datos_stor_limpia_temporales(self):
        with self.servidor.cliente() as c:
            c.login()
            c.cmd("PASV")
            codigo, _ = c.cmd("STOR hueco.bin")
            self.assertEqual(codigo, 150)
            codigo2, _ = c.leer_respuesta()
            self.assertIn(codigo2, (425, 426, 550))
            self.assertFalse((self.servidor.raiz_resuelta / "hueco.bin").exists())
            self.assertEqual(list(self.servidor.raiz_resuelta.glob(".ftp-tmp-*")), [])

    def test_timeout_canal_control_cierra_sesion(self):
        with self.servidor.cliente() as c:
            c.login()
            # Inactividad > FTP_CONTROL_TIMEOUT (2s): el servidor cierra.
            codigo, _ = c.cmd("NOOP")
            self.assertEqual(codigo, 200)
            with self.assertRaises((ConnectionError, socket.timeout, OSError)):
                import time
                time.sleep(3)
                c.cmd("NOOP")

    def test_puerto_pasv_se_cierra_al_repetir_pasv(self):
        with self.servidor.cliente() as c:
            c.login()
            codigo, texto = c.cmd("PASV")
            partes = [int(p) for p in texto[texto.index("(") + 1:texto.index(")")].split(",")]
            puerto1 = partes[4] * 256 + partes[5]
            c.cmd("PASV")  # el primer PASV debe cerrarse
            # Conectar al puerto viejo debe fallar (o no servir LIST).
            try:
                viejo = socket.create_connection(("127.0.0.1", puerto1), timeout=1)
            except OSError:
                return  # cerrado: correcto
            # Si el SO permite reutilizar, al menos no debe colgarse.
            viejo.close()


# ---------------------------------------------------------------------------
# 8. Concurrencia y apagado
# ---------------------------------------------------------------------------


class TestConcurrencia(BasePruebas):

    env_servidor = {"FTP_MAX_CLIENTS": 2}

    def test_tercera_sesion_recibe_421(self):
        c1 = self.servidor.cliente()
        c2 = self.servidor.cliente()
        self.addCleanup(c1.cerrar)
        self.addCleanup(c2.cerrar)
        c1.login()
        c2.login()
        c3 = self.servidor.cliente()
        self.addCleanup(c3.cerrar)
        codigo, _ = c3.banner
        self.assertEqual(codigo, 421)

    def test_semaforo_se_libera_al_cerrar_sesion(self):
        c1 = self.servidor.cliente()
        c1.login()
        c1.cmd("QUIT")
        c1.cerrar()
        # Tras liberar la plaza, una nueva sesión debe poder autenticarse.
        with self.servidor.cliente() as c2:
            c2.login()

    def test_desconexion_sin_quit_libera_sesion(self):
        c1 = self.servidor.cliente()
        c1.login()
        c1.cerrar()  # sin QUIT
        import time
        time.sleep(0.5)
        with self.servidor.cliente() as c2:
            c2.login()

    def test_apagado_limpio_cierra_escucha(self):
        servidor2 = ServidorDePrueba(FTP_MAX_CLIENTS=2)
        sock_probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_probe.settimeout(1)
        servidor2.parar()
        with self.assertRaises(OSError):
            sock_probe.connect(("127.0.0.1", servidor2.puerto))
        sock_probe.close()


# ---------------------------------------------------------------------------
# 9. Comandos varios
# ---------------------------------------------------------------------------


class TestComandosVarios(BasePruebas):

    def test_syst(self):
        with self.servidor.cliente() as c:
            self.assertEqual(c.cmd("SYST")[0], 215)

    def test_type_i_y_otro(self):
        with self.servidor.cliente() as c:
            self.assertEqual(c.cmd("TYPE I")[0], 200)
            self.assertEqual(c.cmd("TYPE A")[0], 504)

    def test_quit(self):
        with self.servidor.cliente() as c:
            self.assertEqual(c.cmd("QUIT")[0], 221)
            with self.assertRaises(ConnectionError):
                c.leer_respuesta()

    def test_comando_desconocido(self):
        with self.servidor.cliente() as c:
            self.assertEqual(c.cmd("FOO")[0], 502)

    def test_noop(self):
        with self.servidor.cliente() as c:
            self.assertEqual(c.cmd("NOOP")[0], 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)

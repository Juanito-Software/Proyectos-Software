"""Pruebas unitarias y de integración del servidor web HTTP.

Usa únicamente la biblioteca estándar (unittest, sockets de loopback,
tempfile y mock). Las pruebas de integración levantan el servidor en el
puerto 0 sobre un directorio temporal, así que no dependen del puerto 8080,
del directorio de trabajo ni de recursos externos.

Ejecutar desde la carpeta del proyecto:

    python -m unittest -v test_servidor_web
"""

import errno
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import servidor_web as sw  # noqa: E402


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def peticion_http(metodo: str, ruta: str, cabeceras_extra: bytes = b"") -> bytes:
    """Construye una petición HTTP/1.1 completa de prueba."""
    linea = f"{metodo} {ruta} HTTP/1.1\r\nHost: prueba\r\n".encode("latin-1")
    return linea + cabeceras_extra + b"Connection: close\r\n\r\n"


def parsear_respuesta(bruto: bytes):
    """Devuelve (codigo, cabeceras, cuerpo) de una respuesta cruda."""
    if not bruto:
        return 0, {}, b""
    cabeceras, _separador, cuerpo = bruto.partition(b"\r\n\r\n")
    lineas = cabeceras.split(b"\r\n")
    partes = lineas[0].split(b" ", 2)
    try:
        codigo = int(partes[1])
    except (IndexError, ValueError):
        codigo = -1
    cab = {}
    for linea in lineas[1:]:
        nombre, _sep, valor = linea.partition(b":")
        cab[nombre.strip().decode("latin-1").lower()] = valor.strip().decode("latin-1")
    return codigo, cab, cuerpo


def solicitar_en(puerto: int, peticion: bytes, fragmentos=None, tiempo: float = 6.0):
    """Envía bytes crudos al servidor y devuelve (codigo, cabeceras, cuerpo)."""
    with socket.create_connection(("127.0.0.1", puerto), timeout=tiempo) as cliente:
        cliente.settimeout(tiempo)
        envios = fragmentos if fragmentos is not None else [peticion]
        try:
            for trozo in envios:
                cliente.sendall(trozo)
                if len(envios) > 1:
                    time.sleep(0.02)
        except OSError:
            pass
        bruto = b""
        while True:
            try:
                trozo = cliente.recv(65536)
            except (TimeoutError, OSError):
                break
            if not trozo:
                break
            bruto += trozo
        return parsear_respuesta(bruto)


class BaseServidorEnPrueba(unittest.TestCase):
    """Sirve un directorio temporal en el puerto 0 para cada prueba."""

    max_clientes = 4
    timeout_conexion = 2.0

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.raiz = os.path.join(self.tmp, "public")
        self.externo = os.path.join(self.tmp, "public_evil")
        os.mkdir(self.raiz)
        os.mkdir(self.externo)

        self.escribir("index.html", "<!DOCTYPE html>\n<html><body>Inicio de pruebas</body></html>\n")
        self.escribir("pagina.txt", "contenido de pagina")
        self.escribir("datos.bin", bytes(range(256)) + b"\x00\xff\xc3\xfe")
        os.mkdir(os.path.join(self.raiz, "sub"))
        self.escribir("sub/index.html", "indice de sub")
        os.mkdir(os.path.join(self.raiz, "sin_index"))
        self.escribir_externo("secreto.txt", "SECRETO-EXTERNO")
        with open(os.path.join(self.tmp, "fuera.txt"), "wb") as flujo:
            flujo.write("FUERA".encode("utf-8"))

        self.servidor = sw.ServidorWeb(
            host="127.0.0.1",
            puerto=0,
            directorio_raiz=self.raiz,
            max_clientes=self.max_clientes,
            timeout_conexion=self.timeout_conexion,
        )
        self.servidor.arrancar()
        self.hilo = threading.Thread(target=self.servidor.servir_bucle, daemon=True)
        self.hilo.start()
        self.addCleanup(self._detener_servidor)

    def _detener_servidor(self):
        self.servidor.detener()
        self.hilo.join(10)
        self.assertFalse(self.hilo.is_alive(), "el hilo del servidor no terminó")

    # -- ayudantes de ficheros ---------------------------------------------

    def escribir(self, nombre: str, contenido):
        ruta = os.path.join(self.raiz, *nombre.split("/"))
        if isinstance(contenido, str):
            contenido = contenido.encode("utf-8")
        with open(ruta, "wb") as flujo:
            flujo.write(contenido)

    def escribir_externo(self, nombre: str, contenido):
        ruta = os.path.join(self.externo, nombre)
        if isinstance(contenido, str):
            contenido = contenido.encode("utf-8")
        with open(ruta, "wb") as flujo:
            flujo.write(contenido)

    def leer(self, nombre: str) -> bytes:
        with open(os.path.join(self.raiz, *nombre.split("/")), "rb") as flujo:
            return flujo.read()

    def solicitar(self, peticion, fragmentos=None, tiempo=None):
        tiempo = 5.0 if tiempo is None else tiempo
        return solicitar_en(self.servidor.puerto_asignado, peticion,
                            fragmentos=fragmentos, tiempo=tiempo)

    def solicitar_reintentando(self, peticion, intentos=40, espera=0.05):
        """Reintenta hasta que el servidor no responda 503 (permiso liberado)."""
        codigo, cab, cuerpo = 0, {}, b""
        for _ in range(intentos):
            codigo, cab, cuerpo = self.solicitar(peticion)
            if codigo != 503:
                return codigo, cab, cuerpo
            time.sleep(espera)
        return codigo, cab, cuerpo

    def crear_enlace(self, nombre: str, destino: str, dir_objetivo=False) -> str:
        """Crea un enlace simbólico en la raíz; omite la prueba si no es posible."""
        enlace = os.path.join(self.raiz, nombre)
        try:
            os.symlink(destino, enlace, target_is_directory=dir_objetivo)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"el sistema no permite crear enlaces simbólicos: {exc}")
        return "/" + nombre


# ---------------------------------------------------------------------------
# Pruebas unitarias de parsing y configuración
# ---------------------------------------------------------------------------

class PruebasDeParseo(unittest.TestCase):
    """parsear_peticion(): gramática, encuadre y límites lógicos."""

    def parsear(self, bloque: bytes) -> sw.Peticion:
        return sw.parsear_peticion(bloque)

    def codigo_de(self, bloque: bytes) -> int:
        try:
            self.parsear(bloque)
        except sw.ErrorPeticion as exc:
            return exc.codigo
        return 200

    def test_parseo_valido_get_con_query(self):
        p = self.parsear(b"GET /hola?x=1&y=2 HTTP/1.1\r\nHost: localhost:8080")
        self.assertEqual(p.metodo, "GET")
        self.assertEqual(p.ruta, "/hola")
        self.assertEqual(p.version, (1, 1))
        self.assertEqual(p.cabeceras["host"], "localhost:8080")

    def test_parseo_valido_head(self):
        p = self.parsear(b"HEAD /pagina.txt HTTP/1.1\r\nHost: x")
        self.assertEqual(p.metodo, "HEAD")
        self.assertEqual(p.ruta, "/pagina.txt")

    def test_parseo_admite_lineas_con_salto_lf(self):
        p = self.parsear(b"GET / HTTP/1.0\nHost: x")
        self.assertEqual(p.version, (1, 0))

    def test_parseo_decodifica_porcentaje(self):
        p = self.parsear(b"GET /a%20b%2Fc HTTP/1.1\r\nHost: x")
        self.assertEqual(p.ruta, "/a b/c")

    def test_bloque_vacio_no_se_convierte_en_get(self):
        self.assertEqual(self.codigo_de(b""), 400)

    def test_basura_no_se_convierte_en_get(self):
        self.assertEqual(self.codigo_de(b"GARBAGE"), 400)
        self.assertEqual(self.codigo_de(b"GARBAGE\r\n\r\n"), 400)

    def test_linea_incompleta_rechazada(self):
        self.assertEqual(self.codigo_de(b"GET /"), 400)
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1 extra\r\nHost: x"), 400)
        self.assertEqual(self.codigo_de(b"GET  / HTTP/1.1\r\nHost: x"), 400)

    def test_version_mal_formada_rechazada(self):
        self.assertEqual(self.codigo_de(b"GET / HTTP/9\r\nHost: x"), 400)
        self.assertEqual(self.codigo_de(b"GET / HTP/1.1\r\nHost: x"), 400)

    def test_version_no_admitida_devuelve_505(self):
        self.assertEqual(self.codigo_de(b"GET / HTTP/2.0\r\nHost: x"), 505)
        self.assertEqual(self.codigo_de(b"GET / HTTP/0.9\r\nHost: x"), 505)

    def test_destino_sin_forma_de_origen_rechazado(self):
        self.assertEqual(self.codigo_de(b"GET http://x/y HTTP/1.1\r\nHost: x"), 400)
        self.assertEqual(self.codigo_de(b"GET * HTTP/1.1\r\nHost: x"), 400)

    def test_metodo_con_caracteres_invalidos_rechazado(self):
        self.assertEqual(self.codigo_de(b"G\tT / HTTP/1.1\r\nHost: x"), 400)
        self.assertEqual(self.codigo_de(b"GET\x00 / HTTP/1.1\r\nHost: x"), 400)

    def test_host_ausente_en_http11_rechazado(self):
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1\r\n"), 400)
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1\r\nX-A: 1"), 400)

    def test_host_ausente_admitido_en_http10(self):
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.0\r\n"), 200)

    def test_host_vacio_o_invalido_rechazado(self):
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1\r\nHost:"), 400)
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1\r\nHost: bad host"), 400)
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1\r\nHost: x@y"), 400)
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1\r\nHost: x:99999"), 400)
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1\r\nHost: \xff"), 400)

    def test_host_duplicado_rechazado(self):
        bloque = b"GET / HTTP/1.1\r\nHost: a\r\nHost: b"
        self.assertEqual(self.codigo_de(bloque), 400)

    def test_content_length_duplicado_rechazado(self):
        bloque = b"GET / HTTP/1.1\r\nHost: x\r\nContent-Length: 0\r\nContent-Length: 0"
        self.assertEqual(self.codigo_de(bloque), 400)
        bloque = b"GET / HTTP/1.1\r\nHost: x\r\nContent-Length: 1\r\nContent-Length: 2"
        self.assertEqual(self.codigo_de(bloque), 400)

    def test_content_length_no_numerico_rechazado(self):
        for valor in (b"abc", b"-1", b"1.5", b"0x10", b"1 2", b""):
            bloque = b"GET / HTTP/1.1\r\nHost: x\r\nContent-Length: " + valor
            self.assertEqual(self.codigo_de(bloque), 400, valor)

    def test_cero_de_content_length_admitido(self):
        bloque = b"GET / HTTP/1.1\r\nHost: x\r\nContent-Length: 0"
        self.assertEqual(self.codigo_de(bloque), 200)

    def test_cuerpo_no_admitido_devuelve_413(self):
        bloque = b"GET / HTTP/1.1\r\nHost: x\r\nContent-Length: 10"
        self.assertEqual(self.codigo_de(bloque), 413)
        bloque = b"GET / HTTP/1.1\r\nHost: x\r\nContent-Length: 999999999999"
        self.assertEqual(self.codigo_de(bloque), 413)

    def test_transfer_encoding_no_soportado_devuelve_501(self):
        bloque = b"GET / HTTP/1.1\r\nHost: x\r\nTransfer-Encoding: chunked"
        self.assertEqual(self.codigo_de(bloque), 501)

    def test_transfer_encoding_con_content_length_devuelve_400(self):
        bloque = (b"GET / HTTP/1.1\r\nHost: x"
                  b"\r\nTransfer-Encoding: chunked\r\nContent-Length: 0")
        self.assertEqual(self.codigo_de(bloque), 400)

    def test_cabecera_plegada_obs_fold_rechazada(self):
        bloque = b"GET / HTTP/1.1\r\nHost: x\r\nX-A: uno\r\n dos"
        self.assertEqual(self.codigo_de(bloque), 400)

    def test_nombre_de_cabecera_invalido_rechazado(self):
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1\r\nHost: x\r\nBad Header: 1"), 400)
        self.assertEqual(self.codigo_de(b"GET / HTTP/1.1\r\nHost: x\r\nSinDosPuntos: 1"[:0]
                                        + b"GET / HTTP/1.1\r\nHost: x\r\nSinDosPuntos 1"), 400)

    def test_valor_con_caracteres_de_control_rechazado(self):
        bloque = b"GET / HTTP/1.1\r\nHost: x\r\nX-A: vale\x01"
        self.assertEqual(self.codigo_de(bloque), 400)
        bloque = b"GET / HTTP/1.1\r\nHost: x\r\nX-A: vale\x7f"
        self.assertEqual(self.codigo_de(bloque), 400)

    def test_cr_suelto_rechazado(self):
        bloque = b"GET / HTTP/1.1\r\nHost: x\rX-A: 1"
        self.assertEqual(self.codigo_de(bloque), 400)

    def test_escape_de_porcentaje_invalido_rechazado(self):
        self.assertEqual(self.codigo_de(b"GET /a%zz HTTP/1.1\r\nHost: x"), 400)
        self.assertEqual(self.codigo_de(b"GET /a%2 HTTP/1.1\r\nHost: x"), 400)

    def test_ruta_con_utf8_invalido_rechazada(self):
        self.assertEqual(self.codigo_de(b"GET /%ff%fe HTTP/1.1\r\nHost: x"), 400)

    def test_ruta_con_nulo_rechazada(self):
        self.assertEqual(self.codigo_de(b"GET /%00x HTTP/1.1\r\nHost: x"), 400)

    def test_longitud_de_uri_validada_en_parseo(self):
        larga = "/" + "a" * (sw.LIMITE_URI - 1)
        self.assertEqual(len(larga.encode()), sw.LIMITE_URI)
        self.assertEqual(self.codigo_de(b"GET " + larga.encode() + b" HTTP/1.1\r\nHost: x"), 200)
        larga = "/" + "a" * sw.LIMITE_URI
        self.assertEqual(len(larga.encode()), sw.LIMITE_URI + 1)
        self.assertEqual(self.codigo_de(b"GET " + larga.encode() + b" HTTP/1.1\r\nHost: x"), 414)


class PruebasDeConfiguracion(unittest.TestCase):
    """validar_configuracion() y constantes de límites."""

    def test_configuracion_valida_devuelve_raiz_canonica(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        raiz = sw.validar_configuracion("127.0.0.1", 0, tmp, 2, 1.0, 5)
        self.assertEqual(raiz, os.path.realpath(tmp))

    def test_configuracion_invalida_rechazada(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        casos = [
            dict(host="", puerto=0, directorio_raiz=tmp, max_clientes=1,
                 timeout_conexion=1.0, backlog=5),
            dict(host="127.0.0.1", puerto=70000, directorio_raiz=tmp, max_clientes=1,
                 timeout_conexion=1.0, backlog=5),
            dict(host="127.0.0.1", puerto=0, directorio_raiz=tmp, max_clientes=0,
                 timeout_conexion=1.0, backlog=5),
            dict(host="127.0.0.1", puerto=0, directorio_raiz=tmp, max_clientes=1,
                 timeout_conexion=0, backlog=5),
            dict(host="127.0.0.1", puerto=0, directorio_raiz=tmp, max_clientes=1,
                 timeout_conexion=-1.0, backlog=5),
            dict(host="127.0.0.1", puerto=0, directorio_raiz=os.path.join(tmp, "no_existe"),
                 max_clientes=1, timeout_conexion=1.0, backlog=5),
            dict(host="127.0.0.1", puerto=0, directorio_raiz=tmp, max_clientes=1,
                 timeout_conexion=1.0, backlog=0),
        ]
        for caso in casos:
            with self.assertRaises(ValueError, msg=caso):
                sw.validar_configuracion(**caso)

    def test_limites_de_recursos_coherentes(self):
        with mock.patch.object(sw, "LIMITE_URI", sw.LIMITE_LINEA_PETICION + 1):
            with self.assertRaises(ValueError):
                sw.validar_configuracion("127.0.0.1", 0, tempfile.gettempdir(),
                                         1, 1.0, 5)
        with mock.patch.object(sw, "LIMITE_CABECERAS", 8):
            with self.assertRaises(ValueError):
                sw.validar_configuracion("127.0.0.1", 0, tempfile.gettempdir(),
                                         1, 1.0, 5)
        with mock.patch.object(sw, "TAMANO_BLOQUE", 0):
            with self.assertRaises(ValueError):
                sw.validar_configuracion("127.0.0.1", 0, tempfile.gettempdir(),
                                         1, 1.0, 5)

    def test_constructor_del_servidor_valida_configuracion(self):
        with self.assertRaises(ValueError):
            sw.ServidorWeb(puerto=65536)
        with self.assertRaises(ValueError):
            sw.ServidorWeb(max_clientes=-1)
        with self.assertRaises(ValueError):
            sw.ServidorWeb(directorio_raiz="/ruta/que/no/existe/nunca")

    def test_obtener_tipo_mime(self):
        self.assertIn("text/html", sw.obtener_tipo_mime("a/b.html"))
        self.assertIn("text/plain", sw.obtener_tipo_mime("a/b.txt"))
        self.assertEqual(sw.obtener_tipo_mime("a/b.png"), "image/png")
        self.assertEqual(sw.obtener_tipo_mime("a/b.dat"), "application/octet-stream")

    def test_la_importacion_no_arranca_el_servidor(self):
        # El módulo ya está importado: comprobar que no hay efectos ocultos
        # más allá de definir constantes y funciones.
        self.assertTrue(callable(sw.main))
        self.assertIsInstance(sw.PUERTO, int)


class PruebasDeErroresDeArchivo(unittest.TestCase):
    """abrir_archivo(): mapeo de errores del sistema a códigos HTTP."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_fichero_inexistente_devuelve_404(self):
        ruta = os.path.join(self.tmp, "no_existe.txt")
        with self.assertRaises(sw.ErrorPeticion) as contexto:
            sw.abrir_archivo(ruta)
        self.assertEqual(contexto.exception.codigo, 404)

    def test_permisos_denegados_devuelven_403(self):
        ruta = os.path.join(self.tmp, "ok.txt")
        with open(ruta, "wb") as flujo:
            flujo.write(b"x")
        with mock.patch.object(sw.os, "open",
                               side_effect=PermissionError(errno.EACCES, "denegado")):
            with self.assertRaises(sw.ErrorPeticion) as contexto:
                sw.abrir_archivo(ruta)
        self.assertEqual(contexto.exception.codigo, 403)

    def test_fallo_de_sistema_no_clasificado_se_propaga(self):
        ruta = os.path.join(self.tmp, "ok.txt")
        with open(ruta, "wb") as flujo:
            flujo.write(b"x")
        with mock.patch.object(sw.os, "open", side_effect=OSError(errno.EIO, "disco")):
            with self.assertRaises(OSError):
                sw.abrir_archivo(ruta)

    def test_abrir_un_directorio_no_devuelve_un_archivo(self):
        with self.assertRaises(sw.ErrorPeticion) as contexto:
            sw.abrir_archivo(self.tmp)
        self.assertEqual(contexto.exception.codigo, 404)


# ---------------------------------------------------------------------------
# Pruebas de integración: rutas y respuestas correctas
# ---------------------------------------------------------------------------

class PruebasDePeticionesBasicas(BaseServidorEnPrueba):
    """GET, HEAD, /hola, ficheros estáticos y respuestas correctas."""

    def test_get_hola(self):
        codigo, cab, cuerpo = self.solicitar(peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 200)
        self.assertIn("Hola desde Python", cuerpo.decode("utf-8"))
        self.assertIn("text/html", cab["content-type"])
        self.assertEqual(cab["connection"], "close")
        self.assertEqual(cab["x-content-type-options"], "nosniff")
        self.assertEqual(int(cab["content-length"]), len(cuerpo))

    def test_get_hola_ignora_la_query(self):
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", "/hola?x=1"))
        self.assertEqual(codigo, 200)

    def test_get_devuelve_el_index(self):
        codigo, _cab, cuerpo = self.solicitar(peticion_http("GET", "/"))
        self.assertEqual(codigo, 200)
        self.assertEqual(cuerpo, self.leer("index.html"))

    def test_get_archivo_estatico(self):
        codigo, cab, cuerpo = self.solicitar(peticion_http("GET", "/pagina.txt"))
        self.assertEqual(codigo, 200)
        self.assertIn("text/plain", cab["content-type"])
        self.assertEqual(cuerpo, self.leer("pagina.txt"))
        self.assertEqual(int(cab["content-length"]), len(cuerpo))

    def test_get_directorio_con_index(self):
        codigo, _cab, cuerpo = self.solicitar(peticion_http("GET", "/sub/"))
        self.assertEqual(codigo, 200)
        self.assertEqual(cuerpo, self.leer("sub/index.html"))

    def test_get_directorio_sin_index_devuelve_404(self):
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", "/sin_index/"))
        self.assertEqual(codigo, 404)

    def test_get_archivo_inexistente_devuelve_404(self):
        codigo, cab, cuerpo = self.solicitar(peticion_http("GET", "/no_existe.txt"))
        self.assertEqual(codigo, 404)
        self.assertIn("text/html", cab["content-type"])
        self.assertIn(b"/no_existe.txt", cuerpo)
        self.assertEqual(int(cab["content-length"]), len(cuerpo))

    def test_get_archivo_binario_bytes_exactos(self):
        codigo, cab, cuerpo = self.solicitar(peticion_http("GET", "/datos.bin"))
        esperado = self.leer("datos.bin")
        self.assertEqual(codigo, 200)
        self.assertEqual(cuerpo, esperado)
        self.assertEqual(int(cab["content-length"]), len(esperado))
        self.assertEqual(cab["content-type"], "application/octet-stream")

    def test_head_hola_sin_cuerpo_con_el_content_length_del_get(self):
        codigo_get, _cab_get, cuerpo_get = self.solicitar(peticion_http("GET", "/hola"))
        codigo_head, cab_head, cuerpo_head = self.solicitar(peticion_http("HEAD", "/hola"))
        self.assertEqual(codigo_get, 200)
        self.assertEqual(codigo_head, 200)
        self.assertEqual(cuerpo_head, b"")
        self.assertEqual(int(cab_head["content-length"]), len(cuerpo_get))

    def test_head_de_archivo_binario_sin_cuerpo(self):
        esperado = self.leer("datos.bin")
        codigo, cab, cuerpo = self.solicitar(peticion_http("HEAD", "/datos.bin"))
        self.assertEqual(codigo, 200)
        self.assertEqual(cuerpo, b"")
        self.assertEqual(int(cab["content-length"]), len(esperado))

    def test_head_de_index_sin_cuerpo(self):
        codigo, cab, cuerpo = self.solicitar(peticion_http("HEAD", "/"))
        self.assertEqual(codigo, 200)
        self.assertEqual(cuerpo, b"")
        self.assertEqual(int(cab["content-length"]), len(self.leer("index.html")))

    def test_head_de_error_404_sin_cuerpo_con_el_mismo_content_length(self):
        codigo_get, _cab, cuerpo_get = self.solicitar(peticion_http("GET", "/no_existe"))
        codigo_head, cab_head, cuerpo_head = self.solicitar(peticion_http("HEAD", "/no_existe"))
        self.assertEqual(codigo_get, 404)
        self.assertEqual(codigo_head, 404)
        self.assertEqual(cuerpo_head, b"")
        self.assertEqual(int(cab_head["content-length"]), len(cuerpo_get))

    def test_head_de_error_403_sin_cuerpo(self):
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", "/../fuera.txt"))
        self.assertEqual(codigo, 403)
        codigo_head, cab_head, cuerpo_head = self.solicitar(
            peticion_http("HEAD", "/../fuera.txt"))
        self.assertEqual(codigo_head, 403)
        self.assertEqual(cuerpo_head, b"")
        self.assertGreater(int(cab_head["content-length"]), 0)

    def test_405_incluye_allow_y_no_convierte_el_metodo_en_get(self):
        codigo, cab, cuerpo = self.solicitar(peticion_http("POST", "/hola"))
        self.assertEqual(codigo, 405)
        self.assertEqual(cab["allow"], "GET, HEAD")
        self.assertIn("Method Not Allowed", cab["content-type"] + cuerpo.decode("utf-8"))
        self.assertEqual(int(cab["content-length"]), len(cuerpo))
        self.assertNotIn("Hola desde Python", cuerpo.decode("utf-8"))

    def test_405_tambien_en_ruta_inexistente(self):
        codigo, cab, _cuerpo = self.solicitar(peticion_http("DELETE", "/no_existe"))
        self.assertEqual(codigo, 405)
        self.assertEqual(cab["allow"], "GET, HEAD")

    def test_405_escapa_html_en_la_ruta(self):
        codigo, _cab, cuerpo = self.solicitar(peticion_http("POST", "/<b>hola"))
        self.assertEqual(codigo, 405)
        texto = cuerpo.decode("utf-8")
        self.assertIn("&lt;b&gt;hola", texto)
        self.assertNotIn("<b>hola", texto)

    def test_404_escapa_html_de_la_ruta(self):
        codigo, _cab, cuerpo = self.solicitar(
            peticion_http("GET", "/<script>alert(1)</script>"))
        self.assertEqual(codigo, 404)
        texto = cuerpo.decode("utf-8")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", texto)
        self.assertNotIn("<script>alert(1)", texto)

    def test_404_escapa_comillas_y_ampersands(self):
        codigo, _cab, cuerpo = self.solicitar(
            peticion_http("GET", '/a"onload="x"&y=z'))
        self.assertEqual(codigo, 404)
        texto = cuerpo.decode("utf-8")
        self.assertIn("&quot;onload=&quot;x&quot;&amp;y=z", texto)

    def test_las_404_no_expone_rutas_absolutas_del_sistema(self):
        _codigo, _cab, cuerpo = self.solicitar(peticion_http("GET", "/no_existe"))
        self.assertNotIn(self.raiz.encode("utf-8"), cuerpo)
        self.assertNotIn(self.tmp.encode("utf-8"), cuerpo)

    def test_las_cabeceras_del_cliente_no_se_reflejan(self):
        codigo, cab, _cuerpo = self.solicitar(
            peticion_http("GET", "/hola",
                          b"X-Reflejo: valor-secreto\r\nReferer: http://interno/\r\n"))
        self.assertEqual(codigo, 200)
        respuesta_completa = " ".join(f"{k}:{v}" for k, v in cab.items())
        self.assertNotIn("valor-secreto", respuesta_completa)
        self.assertNotIn("interno", respuesta_completa)


# ---------------------------------------------------------------------------
# Pruebas de integración: peticiones malformadas y límites
# ---------------------------------------------------------------------------

class PruebasDePeticionesMalformadas(BaseServidorEnPrueba):
    """Respuestas de error ante parsing inválido, límites y fragmentación."""

    def test_basura_no_se_convierte_en_get(self):
        codigo, _cab, _cuerpo = self.solicitar(b"GARBAGE\r\n\r\n")
        self.assertEqual(codigo, 400)

    def test_linea_incompleta_devuelve_400(self):
        codigo, _cab, _cuerpo = self.solicitar(b"GET /\r\n\r\n")
        self.assertEqual(codigo, 400)

    def test_solicitud_vacia_no_recibe_respuesta(self):
        with socket.create_connection(("127.0.0.1", self.servidor.puerto_asignado),
                                      timeout=5) as cliente:
            cliente.shutdown(socket.SHUT_WR)
            bruto = cliente.recv(4096)
        self.assertEqual(bruto, b"")

    def test_solicitud_parcial_no_se_interpreta_completa(self):
        codigo, _cab, _cuerpo = self.solicitar(
            None,
            fragmentos=[b"GET / HTTP/1.1\r\nHost: prueba\r\n"],
            tiempo=6.0)
        self.assertEqual(codigo, 408)

    def test_version_no_admitida_devuelve_505(self):
        codigo, _cab, _cuerpo = self.solicitar(b"GET / HTTP/2.0\r\nHost: x\r\n\r\n")
        self.assertEqual(codigo, 505)

    def test_host_ausente_devuelve_400(self):
        codigo, _cab, _cuerpo = self.solicitar(b"GET / HTTP/1.1\r\n\r\n")
        self.assertEqual(codigo, 400)

    def test_host_duplicado_devuelve_400(self):
        codigo, _cab, _cuerpo = self.solicitar(
            b"GET / HTTP/1.1\r\nHost: a\r\nHost: b\r\n\r\n")
        self.assertEqual(codigo, 400)

    def test_content_length_duplicado_devuelve_400(self):
        codigo, _cab, _cuerpo = self.solicitar(
            b"GET / HTTP/1.1\r\nHost: x\r\nContent-Length: 0\r\nContent-Length: 1\r\n\r\n")
        self.assertEqual(codigo, 400)

    def test_content_length_incompatible_devuelve_400(self):
        codigo, _cab, _cuerpo = self.solicitar(
            b"GET / HTTP/1.1\r\nHost: x\r\nContent-Length: cero\r\n\r\n")
        self.assertEqual(codigo, 400)

    def test_cuerpo_rechazado_con_413(self):
        codigo, cab, cuerpo = self.solicitar(
            b"GET / HTTP/1.1\r\nHost: x\r\nContent-Length: 10\r\n\r\n")
        self.assertEqual(codigo, 413)
        self.assertEqual(int(cab["content-length"]), len(cuerpo))

    def test_transfer_encoding_devuelve_501(self):
        codigo, _cab, _cuerpo = self.solicitar(
            b"GET / HTTP/1.1\r\nHost: x\r\nTransfer-Encoding: chunked\r\n\r\n")
        self.assertEqual(codigo, 501)

    def test_transfer_encoding_mas_content_length_devuelve_400(self):
        codigo, _cab, _cuerpo = self.solicitar(
            b"GET / HTTP/1.1\r\nHost: x\r\nTransfer-Encoding: chunked"
            b"\r\nContent-Length: 5\r\n\r\n")
        self.assertEqual(codigo, 400)

    def test_cabecera_plegada_devuelve_400(self):
        codigo, _cab, _cuerpo = self.solicitar(
            b"GET / HTTP/1.1\r\nHost: x\r\nX-A: uno\r\n dos\r\n\r\n")
        self.assertEqual(codigo, 400)

    def test_uri_en_el_limite_no_da_414(self):
        uri = "/" + "a" * (sw.LIMITE_URI - 1)
        self.assertEqual(len(uri.encode()), sw.LIMITE_URI)
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", uri))
        self.assertEqual(codigo, 404)

    def test_uri_sobre_el_limite_da_414(self):
        uri = "/" + "a" * (sw.LIMITE_URI + 1)
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", uri))
        self.assertEqual(codigo, 414)

    def test_linea_de_peticion_demasiado_larga_da_414(self):
        uri = "/" + "a" * (sw.LIMITE_LINEA_PETICION + 10)
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", uri))
        self.assertEqual(codigo, 414)

    def _cabeceras_de_tamanyo(self, tamanyo_bloque: int) -> bytes:
        """Petición a /hola cuyo bloque de cabeceras mide exactamente el dado."""
        base = peticion_http("GET", "/hola")
        terminador = b"\r\n\r\n"
        bloque_base = base[: -len(terminador)]
        relleno = "X-Pad: " + "a" * (tamanyo_bloque - len(bloque_base) - 13)
        bloque = bloque_base + b"\r\n" + relleno.encode()
        if len(bloque) + len(terminador) != tamanyo_bloque:
            raise AssertionError(f"cálculo erróneo: {len(bloque) + 4} != {tamanyo_bloque}")
        return bloque + terminador

    def test_cabeceras_en_el_limite_exacto_se_admiten(self):
        peticion = self._cabeceras_de_tamanyo(sw.LIMITE_CABECERAS)
        codigo, _cab, cuerpo = self.solicitar(peticion)
        self.assertEqual(codigo, 200)
        self.assertIn("Hola desde Python", cuerpo.decode("utf-8"))

    def test_cabeceras_sobre_el_limite_devuelven_431(self):
        peticion = self._cabeceras_de_tamanyo(sw.LIMITE_CABECERAS + 1)
        codigo, _cab, _cuerpo = self.solicitar(peticion)
        self.assertEqual(codigo, 431)

    def test_demasiadas_cabeceras_devuelven_431(self):
        extras = b"".join(b"X-%03d: v\r\n" % i
                          for i in range(sw.LIMITE_NUMERO_CABECERAS + 5))
        codigo, _cab, _cuerpo = self.solicitar(
            b"GET /hola HTTP/1.1\r\nHost: x\r\n" + extras + b"\r\n")
        self.assertEqual(codigo, 431)

    def test_solicitud_fragmentada_varios_recv(self):
        peticion = peticion_http("GET", "/pagina.txt")
        trozos = [peticion[i:i + 7] for i in range(0, len(peticion), 7)]
        codigo, _cab, cuerpo = self.solicitar(None, fragmentos=trozos, tiempo=6.0)
        self.assertEqual(codigo, 200)
        self.assertEqual(cuerpo, self.leer("pagina.txt"))

    def test_head_de_error_414_sin_cuerpo(self):
        uri_get = "/" + "a" * (sw.LIMITE_URI + 1)
        codigo_get, _cab, cuerpo_get = self.solicitar(peticion_http("GET", uri_get))
        self.assertEqual(codigo_get, 414)
        codigo_head, cab_head, cuerpo_head = self.solicitar(peticion_http("HEAD", uri_get))
        self.assertEqual(codigo_head, 414)
        self.assertEqual(cuerpo_head, b"")
        self.assertEqual(int(cab_head["content-length"]), len(cuerpo_get))

    def test_head_de_error_400_sin_cuerpo(self):
        peticion_get = b"GET /\x01 HTTP/1.1\r\nHost: x\r\n\r\n"
        peticion_head = b"HEAD /\x01 HTTP/1.1\r\nHost: x\r\n\r\n"
        codigo_get, _cab, cuerpo_get = self.solicitar(peticion_get)
        self.assertEqual(codigo_get, 400)
        codigo_head, cab_head, cuerpo_head = self.solicitar(peticion_head)
        self.assertEqual(codigo_head, 400)
        self.assertEqual(cuerpo_head, b"")
        self.assertEqual(int(cab_head["content-length"]), len(cuerpo_get))

    def test_head_de_error_431_sin_cuerpo(self):
        peticion_get = self._cabeceras_de_tamanyo(sw.LIMITE_CABECERAS + 1)
        codigo_get, _cab, cuerpo_get = self.solicitar(peticion_get)
        self.assertEqual(codigo_get, 431)
        peticion_head = peticion_get.replace(b"GET /hola", b"HEAD /hola", 1)
        codigo_head, cab_head, cuerpo_head = self.solicitar(peticion_head)
        self.assertEqual(codigo_head, 431)
        self.assertEqual(cuerpo_head, b"")
        self.assertEqual(int(cab_head["content-length"]), len(cuerpo_get))

    def test_desconexion_inmediata_no_tumba_el_servidor(self):
        for _ in range(5):
            with socket.create_connection(("127.0.0.1", self.servidor.puerto_asignado),
                                          timeout=5) as cliente:
                cliente.close()
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 200)

    def test_desconexion_tras_una_parte_de_las_cabeceras_no_tumba_el_servidor(self):
        with socket.create_connection(("127.0.0.1", self.servidor.puerto_asignado),
                                      timeout=5) as cliente:
            cliente.sendall(b"GET / HTTP/1.1\r\nHo")
            cliente.close()
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 200)

    def test_bytes_basura_no_tumban_el_servidor(self):
        basura = bytes(range(256)) * 8
        codigo, _cab, _cuerpo = self.solicitar(basura, tiempo=6.0)
        self.assertIn(codigo, (0, 400, 414, 431, 408))
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 200)


class PruebasDeClientesLentos(BaseServidorEnPrueba):
    """Plazo total de cabeceras: un cliente lento no retiene recursos."""

    timeout_conexion = 0.6

    def test_cliente_que_drible_las_cabeceras_recibe_408(self):
        """Los bytes llegan a tiempo de recv, pero nunca se completa la petición."""
        cliente = socket.create_connection(
            ("127.0.0.1", self.servidor.puerto_asignado), timeout=5)
        self.addCleanup(cliente.close)
        terminar = threading.Event()

        def drible():
            try:
                for byte in b"GET / HTTP/1.1\r\nHost: prue":
                    if terminar.is_set():
                        return
                    cliente.sendall(bytes([byte]))
                    time.sleep(0.05)
            except OSError:
                return

        hilo = threading.Thread(target=drible, daemon=True)
        hilo.start()
        cliente.settimeout(5.0)
        bruto = b""
        while True:
            try:
                trozo = cliente.recv(4096)
            except (TimeoutError, OSError):
                break
            if not trozo:
                break
            bruto += trozo
        terminar.set()
        hilo.join(5)
        codigo, _cab, _cuerpo = parsear_respuesta(bruto)
        self.assertEqual(codigo, 408)

    def test_cliente_que_no_envia_nada_no_ocupa_respuesta(self):
        with socket.create_connection(("127.0.0.1", self.servidor.puerto_asignado),
                                      timeout=5) as cliente:
            cliente.settimeout(5.0)
            bruto = cliente.recv(4096)
        self.assertEqual(bruto, b"")

    def test_el_servidor_sigue_despues_de_un_cliente_lento(self):
        codigo, _cab, _cuerpo = self.solicitar(
            None,
            fragmentos=[b"GET / HTTP/1.1\r\nHost: prue"],
            tiempo=6.0)
        self.assertEqual(codigo, 408)
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 200)


# ---------------------------------------------------------------------------
# Pruebas de integración: seguridad de rutas
# ---------------------------------------------------------------------------

class PruebasDeSeguridadDeRutas(BaseServidorEnPrueba):
    """Traversal, separadores alternativos, enlaces simbólicos y permisos."""

    def assert_denegado(self, ruta: str):
        codigo, _cab, cuerpo = self.solicitar(peticion_http("GET", ruta))
        self.assertEqual(codigo, 403, ruta)
        self.assertNotIn(b"SECRETO-EXTERNO", cuerpo)
        self.assertNotIn(b"FUERA", cuerpo)

    def test_traversal_con_dos_puntos(self):
        self.assert_denegado("/../fuera.txt")
        self.assert_denegado("/../../../../etc/passwd")

    def test_traversal_tras_un_directorio(self):
        self.assert_denegado("/sub/../../fuera.txt")
        self.assert_denegado("/sin_index/../..//fuera.txt")

    def test_traversal_codificado(self):
        self.assert_denegado("/%2e%2e/fuera.txt")
        self.assert_denegado("/sub/%2e%2e/%2e%2e/fuera.txt")

    def test_separador_alternativo_en_crudo(self):
        self.assert_denegado("/..\\fuera.txt")
        self.assert_denegado("/sub\\..\\..\\fuera.txt")

    def test_separador_alternativo_codificado(self):
        self.assert_denegado("/..%5Cfuera.txt")
        self.assert_denegado("/%2e%2e%5Cfuera.txt")

    def test_ruta_externa_con_prefijo_compartido_de_la_raiz(self):
        # El directorio public_evil comparte el prefijo textual "public":
        # una comparación con startswith() lo daría por dentro de la raíz.
        self.assert_denegado("/../public_evil/secreto.txt")
        self.assert_denegado("/..%2fpublic_evil%2fsecreto.txt")
        self.assert_denegado("/..%5Cpublic_evil%5Csecreto.txt")

    def test_ruta_absoluta_con_unidad_de_disco(self):
        self.assert_denegado("/C:/Windows/win.ini")
        self.assert_denegado("/%43:/Windows/win.ini")
        self.assert_denegado("//C:/Windows/win.ini")

    def test_enlace_simbolico_a_fichero_externo(self):
        ruta = self.crear_enlace("enlace_fuera.txt",
                                 os.path.join(self.tmp, "fuera.txt"))
        self.assert_denegado(ruta)

    def test_enlace_simbolico_a_fichero_interno(self):
        # Política conservadora: también se rechaza si el destino está dentro.
        ruta = self.crear_enlace("enlace_dentro.txt",
                                 os.path.join(self.raiz, "pagina.txt"))
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", ruta))
        self.assertEqual(codigo, 403)

    def test_enlace_simbolico_en_directorio_intermedio(self):
        ruta = self.crear_enlace("dir_externo", self.tmp, dir_objetivo=True)
        self.assert_denegado(ruta + "/fuera.txt")

    def test_enlace_simbolico_roto(self):
        ruta = self.crear_enlace("enlace_roto.txt",
                                 os.path.join(self.tmp, "no_existe_nunca.txt"))
        codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", ruta))
        self.assertEqual(codigo, 403)

    def test_enlace_simbolico_en_el_index_de_un_directorio(self):
        destino = os.path.join(self.tmp, "fuera.txt")
        indice = os.path.join(self.raiz, "sub", "index.html")
        try:
            os.symlink(destino, indice + ".enlace")
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"el sistema no permite crear enlaces simbólicos: {exc}")
        os.remove(indice)
        try:
            os.symlink(destino, indice, target_is_directory=False)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"el sistema no permite crear enlaces simbólicos: {exc}")
        self.assert_denegado("/sub/")

    def test_archivo_sin_permisos_devuelve_403(self):
        ruta = os.path.join(self.raiz, "restringido.txt")
        with open(ruta, "wb") as flujo:
            flujo.write(b"restringido")
        os.chmod(ruta, 0)
        try:
            try:
                with open(ruta, "rb"):
                    pass
            except OSError:
                pass
            else:
                self.skipTest("el sistema operativo no aplica la denegación de "
                              "lectura con chmod 0 (comportamiento de Windows)")
            codigo, cab, cuerpo = self.solicitar(peticion_http("GET", "/restringido.txt"))
            self.assertEqual(codigo, 403)
            self.assertIn("text/html", cab["content-type"])
            self.assertNotIn(b"restringido", cuerpo.replace(b"restringido.txt", b""))
        finally:
            os.chmod(ruta, 0o644)

    def test_fallo_interno_no_filtra_detalles_al_cliente(self):
        with mock.patch.object(sw, "abrir_archivo",
                               side_effect=OSError("fallo interno de disco duro")):
            codigo, _cab, cuerpo = self.solicitar(peticion_http("GET", "/pagina.txt"))
        self.assertEqual(codigo, 500)
        texto = cuerpo.decode("utf-8")
        self.assertNotIn("disco duro", texto)
        self.assertNotIn(self.raiz, texto)
        self.assertIn("500", texto)


# ---------------------------------------------------------------------------
# Pruebas de integración: concurrencia, permisos y cierre
# ---------------------------------------------------------------------------

class PruebasDeConcurrencia(BaseServidorEnPrueba):
    """Límite de clientes simultáneos y liberación de permisos."""

    max_clientes = 1
    timeout_conexion = 1.0

    def test_liberacion_de_permisos_en_peticiones_secuenciales(self):
        # Con un único permiso, si no se liberara tras cada atención, la
        # segunda petición se rechazaría con 503.
        for _ in range(3):
            codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", "/hola"))
            self.assertEqual(codigo, 200)

    def test_limite_de_clientes_simultaneos_devuelve_503(self):
        parcial = b"GET / HTTP/1.1\r\nHost: prueba\r\n"  # sin terminador: retiene el permiso
        primer_cliente = socket.create_connection(
            ("127.0.0.1", self.servidor.puerto_asignado), timeout=5)
        self.addCleanup(primer_cliente.close)
        primer_cliente.sendall(parcial)
        time.sleep(0.1)

        codigo, cab, cuerpo = self.solicitar(peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 503)
        self.assertEqual(cuerpo, b"")
        self.assertEqual(int(cab["content-length"]), 0)
        self.assertEqual(cab["connection"], "close")

        # El primer cliente expira y su permiso se devuelve.
        bruto = b""
        primer_cliente.settimeout(5.0)
        while True:
            try:
                trozo = primer_cliente.recv(4096)
            except (TimeoutError, OSError):
                break
            if not trozo:
                break
            bruto += trozo
        codigo, _cab, _cuerpo = parsear_respuesta(bruto)
        self.assertEqual(codigo, 408)

        codigo, _cab, _cuerpo = self.solicitar_reintentando(
            peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 200)

    def test_fallo_al_iniciar_el_hilo_libera_el_permiso_y_cierra_el_socket(self):
        with mock.patch.object(threading.Thread, "start",
                               side_effect=RuntimeError("sin hilos")):
            codigo, _cab, _cuerpo = self.solicitar(peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 0)  # el socket aceptado se cierra sin respuesta

        codigo, _cab, _cuerpo = self.solicitar_reintentando(
            peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 200)

    def test_rechazos_503_son_pequenos_y_no_identifican_al_cliente(self):
        parcial = b"GET / HTTP/1.1\r\nHost: prueba\r\n"
        primer_cliente = socket.create_connection(
            ("127.0.0.1", self.servidor.puerto_asignado), timeout=5)
        self.addCleanup(primer_cliente.close)
        primer_cliente.sendall(parcial)
        time.sleep(0.1)
        bruto = b""
        with socket.create_connection(("127.0.0.1", self.servidor.puerto_asignado),
                                      timeout=5) as segundo:
            segundo.sendall(peticion_http("GET", "/hola"))
            while True:
                try:
                    trozo = segundo.recv(4096)
                except (TimeoutError, OSError):
                    break
                if not trozo:
                    break
                bruto += trozo
        self.assertLess(len(bruto), 512)
        self.assertNotIn(self.raiz.encode("utf-8"), bruto)


class PruebasDeCierre(BaseServidorEnPrueba):
    """Apagado del servidor sin hilos ni permisos abandonados."""

    def test_cierre_limpio_del_servidor(self):
        servidor = sw.ServidorWeb(host="127.0.0.1", puerto=0,
                                  directorio_raiz=self.raiz)
        puerto = servidor.arrancar()
        hilo = threading.Thread(target=servidor.servir_bucle, daemon=True)
        hilo.start()

        codigo, _cab, _cuerpo = solicitar_en(puerto, peticion_http("GET", "/hola"))
        self.assertEqual(codigo, 200)

        servidor.detener()
        hilo.join(5)
        self.assertFalse(hilo.is_alive(), "el bucle de servicio no terminó")

        with self.assertRaises(OSError):
            socket.create_connection(("127.0.0.1", puerto), timeout=2).close()

    def test_detener_doble_no_lanza_error(self):
        servidor = sw.ServidorWeb(host="127.0.0.1", puerto=0,
                                  directorio_raiz=self.raiz)
        servidor.arrancar()
        servidor.detener()
        servidor.detener()

    def test_arrancar_dos_veces_es_un_error(self):
        servidor = sw.ServidorWeb(host="127.0.0.1", puerto=0,
                                  directorio_raiz=self.raiz)
        servidor.arrancar()
        self.addCleanup(servidor.detener)
        with self.assertRaises(RuntimeError):
            servidor.arrancar()

    def test_servir_sin_arrancar_es_un_error(self):
        servidor = sw.ServidorWeb(host="127.0.0.1", puerto=0,
                                  directorio_raiz=self.raiz)
        with self.assertRaises(RuntimeError):
            servidor.servir_bucle()


if __name__ == "__main__":
    unittest.main()

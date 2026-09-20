"""Tests de helpers puros del módulo visión (sin pantalla, sin LLM, sin OCR)."""
import base64

from tools.vision import _encode_b64, _resolve_tesseract_cmd
from config import CONFIG
from pathlib import Path


class TestEncodeB64:
    def test_codifica_archivo_a_base64(self, tmp_path):
        ruta = tmp_path / "img.png"
        ruta.write_bytes(b"\x89PNG\r\n\x1a\nhola")
        esperado = base64.b64encode(b"\x89PNG\r\n\x1a\nhola").decode("utf-8")
        assert _encode_b64(str(ruta)) == esperado

    def test_codifica_archivo_vacio(self, tmp_path):
        ruta = tmp_path / "vacio.png"
        ruta.write_bytes(b"")
        assert _encode_b64(str(ruta)) == ""


class TestResolveTesseractCmd:
    def test_ruta_explicita_existente_devuelve_esa(self, monkeypatch, tmp_path):
        binario = tmp_path / "tesseract.exe"
        binario.write_bytes(b"PE")
        CONFIG.vision.tesseract_cmd = str(binario)
        # Aunque which/el disco tengan otras rutas, manda la ruta explícita
        monkeypatch.setattr("tools.vision.shutil.which", lambda _: "C:/otra/tesseract.exe")
        try:
            assert _resolve_tesseract_cmd() == str(binario)
        finally:
            CONFIG.vision.tesseract_cmd = None

    def test_sin_ruta_explicita_cae_a_which(self, monkeypatch):
        CONFIG.vision.tesseract_cmd = None
        # convenience: verificar que llama a shutil.which("tesseract")
        llamadas = []

        def _which(cmd):
            llamadas.append(cmd)
            return None  # simular que no está en el PATH

        monkeypatch.setattr("tools.vision.shutil.which", _which)
        monkeypatch.setattr(Path, "is_file", lambda self: False)  # ninguna candidata existe
        try:
            result = _resolve_tesseract_cmd()
            assert "tesseract" in llamadas
            assert result is None
        finally:
            CONFIG.vision.tesseract_cmd = None

    def test_devuelve_algun_localizacion_o_none_sin_crash(self, monkeypatch):
        # En esta máquina Tesseract puede estar instalado o no; el contrato es
        # devolver una ruta str o None, nunca lanzar excepción.
        CONFIG.vision.tesseract_cmd = None
        try:
            resultado = _resolve_tesseract_cmd()
            assert isinstance(resultado, (str, type(None)))
        finally:
            CONFIG.vision.tesseract_cmd = None
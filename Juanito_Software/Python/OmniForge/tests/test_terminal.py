"""Tests de tools de terminal — el fallback subprocess ejecuta comandos reales (sin red)."""
import sys

from tools.terminal import _subprocess_fallback


class TestSubprocessFallback:
    def test_python_ejecuta_codigo(self):
        salida = _subprocess_fallback("print('hola')", "python")
        assert salida == "hola"

    def test_python_devuelve_resultado_de_operacion(self):
        salida = _subprocess_fallback("print(2 + 3)", "python")
        assert salida == "5"

    def test_python_con_error_stderr_se_incluye(self):
        salida = _subprocess_fallback("print('eso va bien'); import no_existe", "python")
        assert "eso va bien" in salida
        assert "STDERR" in salida

    def test_python_sin_salida_devuelve_aviso(self):
        salida = _subprocess_fallback("x = 1", "python")
        assert salida == "(sin salida)"

    def test_shell_ejecuta_comando(self):
        # echo es portable (GNU y Windows)
        salida = _subprocess_fallback("echo hola_mundo", "shell")
        assert "hola_mundo" in salida

    def test_lenguaje_no_soportado_sin_open_interpreter(self):
        salida = _subprocess_fallback("alert(1)", "javascript")
        assert "no soportado" in salida
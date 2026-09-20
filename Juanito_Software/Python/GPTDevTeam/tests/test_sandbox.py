"""Tests del sandbox de ejecución (subprocess real, sin red ni LLM).

Se ejecuta código Python de verdad en un proceso aislado; verifica el
contrato completo: temporales, wrapper de imports, heurística de arranque
y puntuación de la salida."""
import pytest


def _escribir_script(path, codigo):
    path.write_text(codigo, encoding="utf-8")
    return str(path)


class TestSandboxBasico:
    def test_script_que_imprime_termina_con_exito(self, gdt, tmp_path):
        fichero = _escribir_script(tmp_path / "programa.py", "print('hola mundo')")
        estado = gdt.ejecutar_codigo_py(fichero, workspace_dir=str(tmp_path))
        assert estado.exit_code == 0
        assert "hola mundo" in estado.stdout
        assert estado.exec_success is True
        assert estado.termination_reason == "normal"
        assert not estado.stderr

    def test_script_que_falla_assert_tiene_exit_distinto_de_cero(self, gdt, tmp_path):
        fichero = _escribir_script(tmp_path / "falla.py", "assert 1 == 2")
        estado = gdt.ejecutar_codigo_py(fichero, workspace_dir=str(tmp_path))
        assert estado.exit_code != 0
        assert estado.exec_success is False
        assert "AssertionError" in estado.stderr

    def test_script_con_error_de_sintaxis(self, gdt, tmp_path):
        fichero = _escribir_script(tmp_path / "sintaxis.py", "def foo(:\n    pass")
        estado = gdt.ejecutar_codigo_py(fichero, workspace_dir=str(tmp_path))
        assert estado.exit_code != 0
        assert estado.exec_success is False
        assert "SyntaxError" in estado.stderr

    def test_script_con_input_recibe_stdin(self, gdt, tmp_path):
        fichero = _escribir_script(
            tmp_path / "input.py",
            "nombre = input('Nombre: ')\nprint(f'Hola {nombre}')",
        )
        estado = gdt.ejecutar_codigo_py(
            fichero, workspace_dir=str(tmp_path),
            stdin_data="Salir\n",
        )
        assert estado.exec_success is True
        assert "Hola Salir" in estado.stdout


class TestSandboxAislamiento:
    def test_bloquea_imports_peligrosos_desde_main(self, gdt, tmp_path):
        fichero = _escribir_script(tmp_path / "peligro.py", "import os\nprint(os.getcwd())")
        estado = gdt.ejecutar_codigo_py(fichero, workspace_dir=str(tmp_path), block_imports=True)
        assert estado.exec_success is False
        assert "Import" in estado.stderr

    def test_permite_imports_estandar(self, gdt, tmp_path):
        fichero = _escribir_script(tmp_path / "seguro.py", "import math\nprint(math.sqrt(16))")
        estado = gdt.ejecutar_codigo_py(fichero, workspace_dir=str(tmp_path), block_imports=True)
        assert estado.exec_success is True
        assert "4.0" in estado.stdout

    def test_block_imports_false_permite_os(self, gdt, tmp_path):
        fichero = _escribir_script(tmp_path / "libre.py", "import os\nprint('libre')")
        estado = gdt.ejecutar_codigo_py(fichero, workspace_dir=str(tmp_path), block_imports=False)
        assert estado.exec_success is True
        assert "libre" in estado.stdout

    def test_no_deja_temporales_tras_ejecutar(self, gdt, tmp_path):
        fichero = _escribir_script(tmp_path / "programa.py", "print('limpio')")
        gdt.ejecutar_codigo_py(fichero, workspace_dir=str(tmp_path))
        assert not (tmp_path / ".sandbox").exists()


class TestSandboxEvaluacion:
    def test_evaluar_salida_perfecta(self, gdt):
        # exit 0 + stderr limpio + stdout con contenido extra
        assert gdt.evaluar_salida("salida de prueba", "", 0) == 10

    def test_evaluar_salida_con_stderr_limpio_y_sin_stdout(self, gdt):
        assert gdt.evaluar_salida("", "", 0) == 8

    def test_evaluar_salida_penaliza_assertion_error(self, gdt):
        score = gdt.evaluar_salida("", "AssertionError: falló", 1)
        assert score < 5

    def test_evaluar_salida_penaliza_excepcion_general(self, gdt):
        score = gdt.evaluar_salida("", "Traceback (most recent call last)", 1)
        assert score < 8

    def test_evaluar_salida_nunca_negativo(self, gdt):
        assert gdt.evaluar_salida("", "AssertionError\nTraceback" * 3, 1) >= 0


class TestSandboxTemporizacion:
    def test_script_infinito_se_corta_por_timeout(self, gdt, tmp_path):
        fichero = _escribir_script(tmp_path / "infinito.py", "while True:\n    pass")
        # Timeout corto para que el test sea rápido
        estado = gdt.ejecutar_codigo_py(fichero, workspace_dir=str(tmp_path), timeout=2)
        assert estado.termination_reason == "timeout"
        assert estado.forced_stop is True

    def test_script_interactivo_se_rescata_por_heuristica(self, gdt, tmp_path):
        # un programa que imprime y espera input indefinidamente se considera
        # arrancado con éxito tras startup_timeout
        fichero = _escribir_script(
            tmp_path / "interactivo.py",
            "print('Menú principal')\nwhile True:\n    entrada = input()\n    if entrada == 'exit':\n        break",
        )
        estado = gdt.ejecutar_codigo_py(
            fichero, workspace_dir=str(tmp_path),
            timeout=10, startup_timeout=1,
            stdin_data="salir\n",
        )
        assert estado.termination_reason == "startup_heuristic"
        assert estado.exec_success is True
        assert estado.exit_code == 0
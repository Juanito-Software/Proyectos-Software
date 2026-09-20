"""Tests de las funciones puras de parsing y formateo (v2.0).

No requieren Ollama ni red."""
import pytest


class TestExtraerCodigoPuro:
    def test_bloque_markdown_estandar(self, gdt):
        texto = "```python\ndef foo():\n    return 1\n```"
        assert gdt.extraer_codigo_puro(texto) == "def foo():\n    return 1"

    def test_bloque_markdown_con_texto_alrededor(self, gdt):
        texto = "Aquí tienes:\n```python\nprint('hola')\n```\nSaludos."
        assert gdt.extraer_codigo_puro(texto) == "print('hola')"

    def test_sin_delimitadores_quita_comentarios(self, gdt):
        texto = "# esto es un comentario\n# Instrucción: haz algo\ndef foo():\n    return 1"
        resultado = gdt.extraer_codigo_puro(texto)
        assert "comentario" not in resultado
        assert "def foo():" in resultado

    def test_dedent_y_trim_sin_fences(self, gdt):
        texto = "    def foo():\n        return 1\n"
        resultado = gdt.extraer_codigo_puro(texto)
        assert resultado == "def foo():\n    return 1"

    def test_vacio_con_delimitadores_vacios(self, gdt):
        assert gdt.extraer_codigo_puro("```python\n```") == ""


class TestLimpiarDocstringInicial:
    def test_docstring_de_una_linea_se_elimina(self, gdt):
        texto = '"""Saluda a alguien"""\ndef foo():\n    return 1'
        assert gdt.limpiar_docstring_inicial(texto) == "def foo():\n    return 1"

    def test_docstring_multilinea_se_elimina(self, gdt):
        texto = '"""\nDescripción\n"""\ndef foo():\n    return 1'
        assert gdt.limpiar_docstring_inicial(texto) == "def foo():\n    return 1"

    def test_docstring_entre_comillas_simples_se_elimina(self, gdt):
        texto = "'''\nSaluda\n'''\ndef foo():\n    return 1"
        assert gdt.limpiar_docstring_inicial(texto) == "def foo():\n    return 1"

    def test_sin_docstring_no_cambia_nada(self, gdt):
        texto = "def foo():\n    return 1"
        assert gdt.limpiar_docstring_inicial(texto) == texto

    def test_prosa_antes_del_import_se_conserva(self, gdt):
        # Si no hay triple comillas, la prosa previa no se toca
        texto = "Generaré una solución.\nimport os"
        assert gdt.limpiar_docstring_inicial(texto) == texto


class TestExtractJson:
    def test_json_puro(self, gdt):
        assert gdt.extract_json('{"a": 1}') == {"a": 1}

    def test_prosa_antes_del_json(self, gdt):
        texto = 'Aquí va la evaluación:\n{"score_semantico": 9, "cumple_requisitos": true}'
        assert gdt.extract_json(texto) == {"score_semantico": 9, "cumple_requisitos": True}

    def test_sin_json_devuelve_none(self, gdt):
        assert gdt.extract_json("no hay nada aquí") is None

    def test_json_anidado_se_parsea_completo(self, gdt):
        texto = '{"a": {"b": [1, 2, 3]}}'
        assert gdt.extract_json(texto) == {"a": {"b": [1, 2, 3]}}


class TestFormatearInformeEjecucion:
    def test_formatea_todos_los_campos(self, gdt):
        estado = gdt.ExecutionState(
            exit_code=0, stdout="salida", stderr="", execution_score=8.0,
            termination_reason="normal", forced_stop=False, warnings=[],
        )
        informe = gdt.formatear_informe_ejecucion(estado)
        assert "Exit code: 0" in informe
        assert "Execution score: 8.0" in informe
        assert "Exec success: True" in informe
        assert "Forced stop: False" in informe
        assert "Termination reason: normal" in informe
        assert "stdout:" in informe
        assert "stderr:" in informe

    def test_stdout_y_stderr_vacios_se_marcan(self, gdt):
        estado = gdt.ExecutionState(
            exit_code=1, stdout="", stderr="", execution_score=0.0,
            termination_reason="timeout", forced_stop=True, warnings=[],
        )
        informe = gdt.formatear_informe_ejecucion(estado)
        assert "(vacío)" in informe


class TestBuildPrompts:
    def test_refactor_prompt_envuelve_codigo(self, gdt):
        prompt = gdt.build_refactor_prompt("def foo():\n    pass")
        assert "def foo():" in prompt
        assert "```python" in prompt
        assert "Corrige y refactoriza" in prompt

    def test_debug_prompt_incluye_informe_y_historial(self, gdt):
        prompt = gdt.build_debug_prompt(
            "def foo(): pass", "Exit code: 1", ["error anterior 1", "error anterior 2", "error anterior 3", "error anterior 4"]
        )
        assert "def foo():" in prompt
        assert "Exit code: 1" in prompt
        assert "INSTRUCCIONES PARA DEPURAR" in prompt

    def test_debug_prompt_solo_ultimos_tres_errores(self, gdt):
        historial = [f"error {i}" for i in range(6)]
        prompt = gdt.build_debug_prompt("x=1", "informe", historial)
        assert "error 5" in prompt
        assert "error 4" in prompt
        assert "error 3" in prompt
        assert "error 0" not in prompt

    def test_debug_prompt_sin_historial(self, gdt):
        prompt = gdt.build_debug_prompt("x=1", "informe", [])
        assert "Errores previos" not in prompt
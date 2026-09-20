"""Tests del planner multi-agente — parsing de plan y prompts.

No se invoca ningún LLM ni red: se prueban las funciones puras."""
import pytest

from core.planner import (
    _parse_plan,
    _planner_prompt,
    _synthesizer_prompt,
    _fact_extractor_prompt,
)


class TestParsePlan:
    def test_json_valido_parseado_correctamente(self):
        texto = '[{"agent": "coder", "subtask": "escribe un archivo"}, {"agent": "researcher", "subtask": "busca en la web"}]'
        plan = _parse_plan(texto)
        assert len(plan) == 2
        assert plan[0] == {"agent": "coder", "subtask": "escribe un archivo"}
        assert plan[1]["agent"] == "researcher"

    def test_texto_adicional_alrededor_del_json(self):
        texto = (
            "Claro, este es mi plan:\n"
            '[{"agent": "pc_controller", "subtask": "abre el bloc de notas"}]\n'
            "¿Te parece bien?"
        )
        plan = _parse_plan(texto)
        assert plan == [{"agent": "pc_controller", "subtask": "abre el bloc de notas"}]

    def test_json_roto_devuelve_lista_vacia(self):
        texto = '[{"agent": "coder", "subtask": "incompleto"'
        assert _parse_plan(texto) == []

    def test_sin_llaves_devuelve_lista_vacia(self):
        assert _parse_plan("no hay plan aquí") == []

    def test_llaves_en_lugar_de_array_devuelve_lista_vacia(self):
        # El regex [.*?] captura entre corchetes; un objeto aislado no tiene plan
        assert _parse_plan('{"agent": "coder", "subtask": "x"}') == []

    def test_filtra_elementos_sin_agent_o_subtask(self):
        texto = (
            '[{"agent": "coder", "subtask": "válido"},'
            '{"subtask": "sin agente"},'
            '{"agent": "coder"},'
            '"solo un string",'
            "42]"
        )
        plan = _parse_plan(texto)
        assert plan == [{"agent": "coder", "subtask": "válido"}]

    def test_array_vacio_devuelve_vacio(self):
        assert _parse_plan("[]") == []

    def test_saltos_de_linea_dentro_del_json(self):
        texto = '[\n  {"agent": "coder",\n   "subtask": "multi-línea"}\n]'
        assert _parse_plan(texto) == [{"agent": "coder", "subtask": "multi-línea"}]

    def test_tildes_y_caracteres_especiales(self):
        texto = '[{"agent": "researcher", "subtask": "busca \u201cprecios de café arábica\u201d en la web"}]'
        plan = _parse_plan(texto)
        assert plan[0]["subtask"] == "busca \u201cprecios de café arábica\u201d en la web"


class TestPrompts:
    def test_planner_prompt_incluye_agentes_disponibles(self):
        prompt = _planner_prompt("- coder: ejecuta código")
        assert "Mapper" not in prompt
        assert "- coder: ejecuta código" in prompt
        assert "Return ONLY a valid JSON array" in prompt

    def test_synthesizer_prompt_incluye_tarea_y_resultados(self):
        prompt = _synthesizer_prompt("tarea original", ["[coder] paso 1: hecho", "[researcher] paso 2: datos"])
        assert "tarea original" in prompt
        assert "[coder] paso 1: hecho" in prompt
        assert "[researcher] paso 2: datos" in prompt

    def test_synthesizer_prompt_con_resultados_vacios(self):
        prompt = _synthesizer_prompt("tarea", [])
        assert "Agent results:" in prompt

    def test_fact_extractor_prompt_trunca_tarea_a_300(self):
        tarea_larga = "x" * 500
        prompt = _fact_extractor_prompt(tarea_larga, "resultado corto")
        assert "x" * 300 in prompt
        assert "x" * 301 not in prompt
        assert "resultado corto" in prompt

    def test_fact_extractor_prompt_trunca_resultado_a_500(self):
        resultado_largo = "y" * 900
        prompt = _fact_extractor_prompt("tarea", resultado_largo)
        assert "y" * 500 in prompt
        assert "y" * 501 not in prompt

    def test_fact_extractor_prompt_exige_json(self):
        prompt = _fact_extractor_prompt("tarea", "resultado")
        assert "JSON array" in prompt
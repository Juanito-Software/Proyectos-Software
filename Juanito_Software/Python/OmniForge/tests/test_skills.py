"""Tests del cargador de skills y de la fusión de tools."""
from pathlib import Path

import pytest

from core.skills import load_skills, merge_skills, _SKILLS_CACHE


def _reset_cache():
    import core.skills
    core.skills._SKILLS_CACHE = None


@pytest.fixture(autouse=True)
def cache_limpia():
    _reset_cache()
    yield
    _reset_cache()


def _crear_skill(dir_skills: Path, nombre: str, contenido: str):
    (dir_skills / f"{nombre}.py").write_text(contenido, encoding="utf-8")


class TestLoadSkills:
    def test_carga_skills_de_un_directorio(self, tmp_path):
        _crear_skill(
            tmp_path, "saludo",
            """from langchain_core.tools import tool

@tool
def say_hello(nombre: str) -> str:
    \"\"\"Saluda a alguien.\"\"\"
    return f"Hola {nombre}"
""",
        )
        mapa = load_skills(tmp_path)
        assert "*" in mapa
        nombres = {t.name for t in mapa["*"]}
        assert "say_hello" in nombres

    def test_respeta_skill_metadata_de_agentes(self, tmp_path):
        _crear_skill(
            tmp_path, "solo_coder",
            """from langchain_core.tools import tool

SKILL_METADATA = {"agents": ["coder"]}

@tool
def compilar_codigo(codigo: str) -> str:
    \"\"\"Compila código.\"\"\"
    return "ok"
""",
        )
        mapa = load_skills(tmp_path)
        assert "coder" in mapa
        assert "pc_controller" not in mapa
        assert "*" not in mapa

    def test_ignora_archivos_que_empiezan_por_guion_bajo(self, tmp_path):
        _crear_skill(
            tmp_path, "_oculpa",
            """from langchain_core.tools import tool

@tool
def tool_oculta() -> str:
    \"\"\"No debería cargarse.\"\"\"
    return "x"
""",
        )
        mapa = load_skills(tmp_path)
        assert mapa == {}

    def test_app_vacio_si_el_directorio_no_existe(self, tmp_path):
        mapa = load_skills(tmp_path / "no_existe")
        assert mapa == {}

    def test_errores_de_import_no_rompen_la_suite(self, tmp_path):
        _crear_skill(tmp_path, "roto", "import modulo_que_no_existe\nfoo = bar")
        _crear_skill(
            tmp_path, "bueno",
            """from langchain_core.tools import tool

@tool
def buena_skill() -> str:
    \"\"\"Skill válida.\"\"\"
    return "ok"
""",
        )
        mapa = load_skills(tmp_path)
        assert "*" in mapa
        assert "buena_skill" in {t.name for t in mapa["*"]}

    def test_resultado_se_cachea(self, tmp_path):
        _crear_skill(
            tmp_path, "saludo",
            """from langchain_core.tools import tool

@tool
def say_hello() -> str:
    \"\"\"Saluda.\"\"\"
    return "Hola"
""",
        )
        primera = load_skills(tmp_path)
        # El mismo resultado sin reescaneo de disco
        (tmp_path / "saludo.py").unlink()
        segunda = load_skills(tmp_path)
        assert segunda is primera


class TestMergeSkills:
    class _FakeTool:
        def __init__(self, nombre):
            self.name = nombre

    def test_no_duplica_tools_por_nombre(self):
        base = [self._FakeTool("tool_a"), self._FakeTool("tool_b")]
        skills = {"*": [self._FakeTool("tool_a"), self._FakeTool("skill_x")]}
        fusionado = merge_skills(base, skills, "coder")
        nombres = [t.name for t in fusionado]
        assert nombres == ["tool_a", "tool_b", "skill_x"]

    def test_aplica_skills_de_agente_especifico(self):
        base = []
        skills = {
            "*": [self._FakeTool("comun")],
            "coder": [self._FakeTool("solo_coder")],
            "researcher": [self._FakeTool("solo_researcher")],
        }
        fusionado = merge_skills(base, skills, "coder")
        assert {t.name for t in fusionado} == {"comun", "solo_coder"}

    def test_respeta_fuente_de_verdad_de_skill_metadatos(self):
        base = []
        skills = {"*": [self._FakeTool("comun")], "coder": [self._FakeTool("x")]}
        fusionado = merge_skills(base, skills, "pc_controller")
        assert {t.name for t in fusionado} == {"comun"}
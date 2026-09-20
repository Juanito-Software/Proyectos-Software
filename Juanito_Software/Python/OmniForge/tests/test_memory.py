"""Tests de la memoria persistente — tareas, hechos, hints, persistencia y migración."""
import json

import pytest

from core.memory import MemoryStore


class TestTareas:
    def test_add_guarda_y_persiste(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        memoria.add("tarea 1", "resultado 1", ["coder"])
        memoria.add("tarea 2", "resultado 2", ["researcher"])

        recargada = MemoryStore(path=str(tmp_path / "memory.json"))
        assert len(recargada) == 2
        assert recargada._tasks[0]["task"] == "tarea 1"
        assert recargada._tasks[1]["result"] == "resultado 2"

    def test_respeta_max_entries(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"), max_entries=3)
        for i in range(10):
            memoria.add(f"tarea {i}", "ok")
        assert len(memoria) == 3
        # conserva las más recientes
        assert memoria._tasks[0]["task"] == "tarea 7"
        assert memoria._tasks[-1]["task"] == "tarea 9"

    def test_agentes_por_defecto_vacio(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        memoria.add("tarea", "ok")
        assert memoria._tasks[0]["agents_used"] == []

    def test_get_context_sin_datos_devuelve_none(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        assert memoria.get_context() is None

    def test_get_context_incluye_tareas_con_timestamp(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        memoria.add("abrir notepad", "listo", ["pc_controller"])
        contexto = memoria.get_context()
        assert "abrir notepad" in contexto
        assert "pc_controller" in contexto
        assert len(contexto) <= memoria.max_context_chars

    def test_get_context_trunca_a_max_context_chars(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"), max_context_chars=300)
        memoria.add("tarea corta", "resultado corto", ["coder"])
        contexto = memoria.get_context()
        assert contexto is not None
        assert len(contexto) <= 300


class TestHechos:
    def test_add_fact_guarda_y_rechaza_duplicados(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        assert memoria.add_fact("Chrome instalado en Program Files") is True
        # duplicado exacto
        assert memoria.add_fact("Chrome instalado en Program Files") is False
        # substring relacionado
        assert memoria.add_fact("chrome instalado en program files") is False
        assert len(memoria.facts) == 1

    def test_fact_vacio_se_ignora(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        assert memoria.add_fact("   ") is False
        assert memoria.facts == []

    def test_add_facts_guarda_en_lote_y_devuelve_solo_anadidos(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        anadidos = memoria.add_facts(["facto 1", "facto 1", "facto 2"])
        assert anadidos == ["facto 1", "facto 2"]
        assert memoria.facts == ["facto 1", "facto 2"]

    def test_max_facts_recorta_hechos(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"), max_facts=3)
        for i in range(6):
            memoria.add_fact(f"hecho {i}")
        assert len(memoria.facts) == 3
        assert memoria.facts[0] == "hecho 3"

    def test_facts_persisten_entre_instancias(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        memoria.add_fact("user prefiere VSCode")
        recargada = MemoryStore(path=str(tmp_path / "memory.json"))
        assert recargada.facts == ["user prefiere VSCode"]


class TestHints:
    def test_add_hint_guarda_y_deduplica_independientemente_de_facts(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        # Same texto como fact y como hint: ambos viven, no se bloquean
        assert memoria.add_fact("usa sleep tras lanzar apps") is True
        assert memoria.add_hint("usa sleep tras lanzar apps") is True
        assert memoria.facts == ["usa sleep tras lanzar apps"]
        assert memoria.hints == ["usa sleep tras lanzar apps"]
        # duplicado dentro de hints
        assert memoria.add_hint("usa sleep tras lanzar apps") is False

    def test_hint_vacio_se_ignora(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        assert memoria.add_hint("") is False
        assert memoria.hints == []

    def test_get_context_incluye_hints_en_seccion_propia(self, tmp_path):
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        memoria.add_hint("siempre verifica URL con get_current_url")
        contexto = memoria.get_context()
        assert "PLANNING HINTS" in contexto
        assert "siempre verifica URL" in contexto


class TestMigracion:
    def test_migra_hints_mezclados_en_facts_antiguos(self, tmp_path):
        ruta = tmp_path / "memory.json"
        # Simula un memory.json pre-P4 con [HINT] mezclados en "facts"
        ruta.write_text(json.dumps({
            "tasks": [{"id": "1", "timestamp": "2026-01-01T00:00:00",
                       "task": "t", "result": "r", "agents_used": []}],
            "facts": ["[HINT] usa sleep tras lanzar apps", "hecho normal"],
            "hints": [],
        }), encoding="utf-8")

        memoria = MemoryStore(path=str(ruta))
        assert memoria.hints == ["usa sleep tras lanzar apps"]
        assert memoria.facts == ["hecho normal"]

    def test_carga_formato_lista_antiguo(self, tmp_path):
        ruta = tmp_path / "memory.json"
        ruta.write_text(json.dumps([
            {"id": "1", "timestamp": "2026-01-01T00:00:00",
             "task": "tarea antigua", "result": "ok", "agents_used": []}
        ]), encoding="utf-8")

        memoria = MemoryStore(path=str(ruta))
        assert len(memoria) == 1
        assert memoria._tasks[0]["task"] == "tarea antigua"
        assert memoria.facts == []
        assert memoria.hints == []

    def test_json_corrupto_se_recupera_sin_error(self, tmp_path):
        ruta = tmp_path / "memory.json"
        ruta.write_text("{ esto no es json", encoding="utf-8")
        memoria = MemoryStore(path=str(ruta))
        assert len(memoria) == 0


class TestRepeticionDeEscritura:
    def test_escrituras_no_pierden_datos_entre_hilos(self, tmp_path):
        import threading
        memoria = MemoryStore(path=str(tmp_path / "memory.json"))
        errores = []

        def anadir(i):
            try:
                for j in range(5):
                    memoria.add(f"hilo {i} tarea {j}", "ok")
            except Exception as e:
                errores.append(e)

        hilos = [threading.Thread(target=anadir, args=(i,)) for i in range(4)]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()

        assert not errores
        assert len(memoria) == 20
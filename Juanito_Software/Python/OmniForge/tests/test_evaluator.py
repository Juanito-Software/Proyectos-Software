"""Tests del evaluador de tareas — clasificación de fallos, eficiencia y análisis.

No se invoca ningún LLM real en evaluate()/save()/summary(); analyze_and_generate_hint
usa un LLM falso para verificar el contrato HINT:/NO_PATTERN."""
from pathlib import Path

import pytest

from core.evaluator import (
    Evaluator,
    TaskEvaluation,
    FAILURE_NONE,
    FAILURE_TIMEOUT,
    FAILURE_TOOL_ERRORS,
    FAILURE_WRONG_AGENT,
    FAILURE_PLAN_EMPTY,
)


class TestEvaluadorPuro:
    """Evalúa sin persistir — evaluar() no toca disco hasta save()."""

    def _nuevo(self, tmp_path) -> Evaluator:
        return Evaluator(eval_dir=str(tmp_path), analyze_every=10)

    def test_fallo_por_plan_vacio(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        ev = evaluador.evaluate(
            task="tarea", plan=[], results=[], iterations=1, max_iterations=20
        )
        assert ev.failure_type == FAILURE_PLAN_EMPTY
        assert ev.plan_steps == 0

    def test_fallo_por_timeout(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        plan = [{"agent": "coder", "subtask": "x"}]
        ev = evaluador.evaluate(
            task="tarea", plan=plan, results=["ok"], iterations=20, max_iterations=20
        )
        assert ev.failure_type == FAILURE_TIMEOUT

    def test_fallo_por_errores_de_herramientas(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        plan = [{"agent": "coder", "subtask": "x"}, {"agent": "researcher", "subtask": "y"}]
        results = [
            "[coder] paso 1: ERROR: no existe",
            "[researcher] paso 2: ERROR: timeout",
            "[researcher] paso 3: ok",
        ]
        ev = evaluador.evaluate(
            task="tarea", plan=plan, results=results, iterations=3, max_iterations=20
        )
        assert ev.failure_type == FAILURE_TOOL_ERRORS
        assert ev.error_count == 2

    def test_fallo_por_agente_inadecuado(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        plan = [{"agent": "coder", "subtask": "x"}]
        results = ["[coder] paso 1: ERROR: no sé hacerlo"]
        ev = evaluador.evaluate(
            task="tarea", plan=plan, results=results, iterations=2, max_iterations=20
        )
        assert ev.failure_type == FAILURE_WRONG_AGENT

    def test_sin_fallo(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        plan = [{"agent": "coder", "subtask": "x"}]
        ev = evaluador.evaluate(
            task="tarea", plan=plan, results=["[coder] paso 1: listo"], iterations=2, max_iterations=20
        )
        assert ev.failure_type == FAILURE_NONE

    def test_eficiencia_perfecta_con_zero_iteraciones(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        ev = evaluador.evaluate(
            task="tarea", plan=[{"agent": "coder", "subtask": "x"}],
            results=["ok"], iterations=0, max_iterations=20
        )
        assert ev.efficiency == 1.0

    def test_eficiencia_penalizada_por_iteraciones(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        ev = evaluador.evaluate(
            task="tarea", plan=[{"agent": "coder", "subtask": "x"}],
            results=["ok"], iterations=10, max_iterations=20
        )
        assert ev.efficiency < 1.0
        assert 0.0 <= ev.efficiency <= 1.0

    def test_eficiencia_penalizada_por_errores(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        ev = evaluador.evaluate(
            task="tarea", plan=[{"agent": "coder", "subtask": "x"}],
            results=["ERROR: boom", "ERROR: otra vez"],
            iterations=1, max_iterations=20
        )
        # penaliza 0.4 de errores + iteraciones
        assert ev.efficiency <= 0.6

    def test_agentes_usados_se_deduplican(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        plan = [
            {"agent": "coder", "subtask": "a"},
            {"agent": "coder", "subtask": "b"},
            {"agent": "researcher", "subtask": "c"},
        ]
        ev = evaluador.evaluate(
            task="tarea", plan=plan, results=["ok"], iterations=1, max_iterations=20
        )
        assert sorted(ev.agents_used) == ["coder", "researcher"]

    def test_tarea_truncada_a_200_caracteres(self, tmp_path):
        evaluador = self._nuevo(tmp_path)
        ev = evaluador.evaluate(
            task="t" * 500, plan=[{"agent": "coder", "subtask": "x"}],
            results=["ok"], iterations=1, max_iterations=20
        )
        assert len(ev.task) == 200


class TestEvaluadorDisco:
    def test_save_y_load_recent_persisten_en_jsonl(self, tmp_path):
        evaluador = Evaluator(eval_dir=str(tmp_path), analyze_every=10)
        ev = evaluador.evaluate(
            task="tarea guardada", plan=[{"agent": "coder", "subtask": "x"}],
            results=["ok"], iterations=2, max_iterations=20
        )
        evaluador.save(ev)

        # Un segundo Evaluator sobre el mismo dir lee el histórico
        evaluador2 = Evaluator(eval_dir=str(tmp_path), analyze_every=10)
        assert evaluador2._count == 1
        recientes = evaluador2.load_recent(30)
        assert len(recientes) == 1
        assert recientes[0]["task"] == "tarea guardada"

    def test_load_recent_limita_a_n(self, tmp_path):
        evaluador = Evaluator(eval_dir=str(tmp_path), analyze_every=10)
        for i in range(5):
            ev = evaluador.evaluate(
                task=f"tarea {i}", plan=[{"agent": "coder", "subtask": "x"}],
                results=["ok"], iterations=1, max_iterations=20
            )
            evaluador.save(ev)
        recientes = evaluador.load_recent(2)
        assert len(recientes) == 2
        assert recientes[-1]["task"] == "tarea 4"

    def test_should_analyze_al_cumplir_cada_n(self, tmp_path):
        # analyze_every=3 → se analiza tras las tareas 3 y 6
        evaluador = Evaluator(eval_dir=str(tmp_path), analyze_every=3)
        for i in range(6):
            ev = evaluador.evaluate(
                task=f"tarea {i}",
                plan=[{"agent": "coder", "subtask": "x"}],
                results=["ok"], iterations=1, max_iterations=20
            )
            evaluador.save(ev)
            if i in (2, 5):
                assert evaluador.should_analyze()
            else:
                assert not evaluador.should_analyze()

    def test_should_analyze_falso_sin_historial(self, tmp_path):
        evaluador = Evaluator(eval_dir=str(tmp_path), analyze_every=3)
        assert not evaluador.should_analyze()

    def test_summary_estadisticas(self, tmp_path):
        evaluador = Evaluator(eval_dir=str(tmp_path), analyze_every=10)
        # 1 fallo de 3 → failure_rate ~0.33
        for i, fallo in enumerate([True, False, False]):
            ev = evaluador.evaluate(
                task=f"tarea {i}", plan=[{"agent": "coder", "subtask": "x"}],
                results=["ERROR: fallo"] if fallo else ["ok"],
                iterations=1, max_iterations=20
            )
            evaluador.save(ev)
        resumen = evaluador.summary()
        assert resumen["total"] == 3
        assert resumen["avg_efficiency"] > 0
        assert resumen["failure_rate"] == pytest.approx(1 / 3, abs=0.01)
        assert "wrong_agent" in resumen["failure_breakdown"]

    def test_summary_vacio_sin_historial(self, tmp_path):
        evaluador = Evaluator(eval_dir=str(tmp_path), analyze_every=10)
        assert evaluador.summary() == {"total": 0}

    def test_guardado_es_append_only(self, tmp_path):
        evaluador = Evaluator(eval_dir=str(tmp_path), analyze_every=10)
        for i in range(3):
            ev = evaluador.evaluate(
                task=f"tarea {i}", plan=[{"agent": "coder", "subtask": "x"}],
                results=["ok"], iterations=1, max_iterations=20
            )
            evaluador.save(ev)
        lineas = (tmp_path / "evaluations.jsonl").read_text(encoding="utf-8").splitlines()
        assert len(lineas) == 3


class _LLMFalso:
    """Falso LLM que devuelve una respuesta fija con contrato de .content."""

    def __init__(self, respuesta: str):
        self.respuesta = respuesta
        self.llamadas = 0

    def invoke(self, mensajes):
        self.llamadas += 1
        class _Respuesta:
            content = self.respuesta
        return _Respuesta()


class TestAnalisisPatrones:
    def _evaluador_con_historial(self, tmp_path, n: int):
        evaluador = Evaluator(eval_dir=str(tmp_path), analyze_every=10)
        for i in range(n):
            ev = evaluador.evaluate(
                task=f"tarea {i}", plan=[{"agent": "coder", "subtask": "x"}],
                results=["ok"], iterations=1, max_iterations=20
            )
            evaluador.save(ev)
        return evaluador

    def test_no_analiza_con_menos_de_5_evaluaciones(self, tmp_path):
        evaluador = self._evaluador_con_historial(tmp_path, 4)
        llm = _LLMFalso("HINT: prueba")
        assert evaluador.analyze_and_generate_hint(llm) is None
        assert llm.llamadas == 0

    def test_devuelve_hint_cuando_llm_empieza_con_hint(self, tmp_path):
        evaluador = self._evaluador_con_historial(tmp_path, 6)
        llm = _LLMFalso("  HINT: usa sleep_seconds(2) tras lanzar apps  extra  ")
        hint = evaluador.analyze_and_generate_hint(llm)
        assert hint.startswith("usa sleep_seconds")
        assert len(hint) <= 120
        assert "HINT:" not in hint

    def test_devuelve_none_si_llm_dice_no_pattern(self, tmp_path):
        evaluador = self._evaluador_con_historial(tmp_path, 6)
        llm = _LLMFalso("NO_PATTERN")
        assert evaluador.analyze_and_generate_hint(llm) is None

    def test_devuelve_none_si_llm_ignora_el_contrato(self, tmp_path):
        evaluador = self._evaluador_con_historial(tmp_path, 6)
        llm = _LLMFalso("respuesta rara")
        assert evaluador.analyze_and_generate_hint(llm) is None

    def test_format_para_analisis_incluye_campos_clave(self, tmp_path):
        evaluador = self._evaluador_con_historial(tmp_path, 3)
        texto = evaluador._format_for_analysis(evaluador.load_recent(30))
        assert "agents=" in texto
        assert "steps=" in texto
        assert "iters=" in texto
        assert "errors=" in texto
        assert "fail=" in texto
        assert "eff=" in texto


class TestTaskEvaluationDataclass:
    def test_asdict_funciona_para_serializar(self):
        ev = TaskEvaluation(
            id="123", timestamp="2026-01-01T00:00:00", task="tarea",
            plan_steps=1, iterations=2, max_iterations=10,
            error_count=0, agents_used=["coder"],
            failure_type=None, efficiency=0.9,
        )
        import dataclasses
        d = dataclasses.asdict(ev)
        assert d["task"] == "tarea"
        assert d["failure_type"] is None
        assert d["efficiency"] == 0.9
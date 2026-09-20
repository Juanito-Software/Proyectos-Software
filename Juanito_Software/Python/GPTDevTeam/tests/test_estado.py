"""Tests del estado canónico y de los puntos de decisión del pipeline (v2.0).

No requieren Ollama ni red: son dataclasses y propiedades algebraicas puras."""
import pytest


def _execution(test_mask, main_mask, score_test=5.0, score_main=5.0,
               warned=False, semantic=None):
    """Construye un EvaluationState sintético según una máscara de éxito."""
    gdt = pytest.importorskip("gptdevteam_v2")
    test = gdt.ExecutionState(
        exit_code=0 if test_mask else 1,
        stdout="salida" if test_mask else "",
        stderr="" if test_mask else "AssertionError",
        execution_score=score_test,
        termination_reason="normal",
        forced_stop=False,
        warnings=[],
    )
    main = gdt.ExecutionState(
        exit_code=0 if main_mask else 1,
        stdout="salida" if main_mask else "",
        stderr="" if main_mask else "Traceback",
        execution_score=score_main,
        termination_reason="normal",
        forced_stop=False,
        warnings=[],
    )
    sems = {"score_semantico": 8, "cumple_requisitos": True}
    if semantic:
        sems.update(semantic)
    evaluacion = gdt.EvaluationState(
        test_state=test, main_state=main, semantic=sems,
        warnings=["advertencia"] if warned else [],
    )
    return evaluacion, gdt


class TestExecutionState:
    def test_exit_code_cero_es_exito(self, gdt):
        estado = gdt.ExecutionState(
            exit_code=0, stdout="ok", stderr="", execution_score=8.0,
            termination_reason="normal", forced_stop=False, warnings=[],
        )
        assert estado.exec_success is True
        assert estado.execution_quality == 8.0

    def test_exit_code_distinto_de_cero_no_es_exito(self, gdt):
        estado = gdt.ExecutionState(
            exit_code=1, stdout="", stderr="boom", execution_score=0.0,
            termination_reason="normal", forced_stop=False, warnings=[],
        )
        assert estado.exec_success is False

    def test_terminacion_por_timeout_no_es_exito(self, gdt):
        estado = gdt.ExecutionState(
            exit_code=15, stdout="", stderr="", execution_score=0.0,
            termination_reason="timeout", forced_stop=True, warnings=[],
        )
        assert estado.exec_success is False
        assert estado.forced_stop is True


class TestEvaluationMetrics:
    def test_score_exec_media_de_ambos(self, gdt):
        evaluacion, _ = _execution(True, True, score_test=8.0, score_main=4.0)
        metricas = gdt.EvaluationMetrics(evaluacion)
        assert metricas.score_exec == 6.0

    def test_semantic_score_lee_del_juez(self, gdt):
        evaluacion, _ = _execution(True, True, semantic={"score_semantico": 9})
        metricas = gdt.EvaluationMetrics(evaluacion)
        assert metricas.semantic_score == 9.0

    def test_semantic_score_por_defecto_seis(self, gdt):
        evaluacion, _ = _execution(True, True, semantic={"score_semantico": 6})
        metricas = gdt.EvaluationMetrics(evaluacion)
        assert metricas.semantic_score == 6.0

    def test_global_score_promedia_ejecucion_y_semantica(self, gdt):
        evaluacion, _ = _execution(True, True, score_test=10.0, score_main=10.0,
                                   semantic={"score_semantico": 6})
        metricas = gdt.EvaluationMetrics(evaluacion)
        assert metricas.score_exec == 10.0
        assert metricas.global_score == 8.0


class TestEvaluationDecision:
    def test_exito_total(self, gdt):
        evaluacion, _ = _execution(True, True)
        decision = gdt.EvaluationDecision(evaluacion, gdt.EvaluationMetrics(evaluacion))
        assert decision.runtime_success is True
        assert decision.semantic_success is True
        assert decision.clean is True
        assert decision.success is True

    def test_fallo_runtime_con_semantica_ok_no_es_exito(self, gdt):
        evaluacion, _ = _execution(False, True)
        decision = gdt.EvaluationDecision(evaluacion, gdt.EvaluationMetrics(evaluacion))
        assert decision.runtime_success is False
        assert decision.success is False

    def test_semantica_baja_impide_exito(self, gdt):
        evaluacion, _ = _execution(True, True, semantic={"score_semantico": 5})
        decision = gdt.EvaluationDecision(evaluacion, gdt.EvaluationMetrics(evaluacion))
        assert decision.semantic_success is False
        assert decision.success is False

    def test_cumple_requisitos_falso_impide_exito(self, gdt):
        evaluacion, _ = _execution(True, True, semantic={"cumple_requisitos": False})
        decision = gdt.EvaluationDecision(evaluacion, gdt.EvaluationMetrics(evaluacion))
        assert decision.semantic_success is False
        assert decision.success is False

    def test_advertencias_ast_ensucian_pero_no_fallan_runtime(self, gdt):
        evaluacion, _ = _execution(True, True, warned=True)
        decision = gdt.EvaluationDecision(evaluacion, gdt.EvaluationMetrics(evaluacion))
        assert decision.clean is False
        assert decision.runtime_success is True
        assert decision.success is False


class TestConstantesPipeline:
    def test_times_y_scores_tienen_valores_sensatos(self, gdt):
        assert gdt.TIMEOUT_EJECUCION == 30
        assert gdt.TIMEOUT_ARRANQUE == 10
        assert gdt.SCORE_MINIMO_EXITO == 8

    def test_modelos_por_rol_definidos(self, gdt):
        roles = {"planner", "coder", "tester", "judge", "reflector", "documenter"}
        assert roles == set(gdt.MODEL_ROLES.keys())
        assert gdt.MODEL_ROLES["coder"] == "qwen2.5-coder:7b"
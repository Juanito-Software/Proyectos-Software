"""Tests de main.py — construcción de estados iniciales y run() con fakes."""
from main import run, _build_planner_initial_state, _build_agent_initial_state


class TestEstadosIniciales:
    def test_planner_initial_state(self):
        estado = _build_planner_initial_state("tarea de prueba")
        assert estado == {
            "messages": [],
            "task": "tarea de prueba",
            "plan": [],
            "plan_step": 0,
            "results": [],
            "status": None,
            "iteration": 0,
        }

    def test_agent_initial_state_sin_memoria(self):
        estado = _build_agent_initial_state("tarea")
        assert estado["task"] == "tarea"
        assert estado["iteration"] == 0
        assert estado["error_count"] == 0
        assert estado["status"] is None
        assert len(estado["messages"]) == 1

    def test_agent_initial_state_con_memoria_inyecta_contexto(self):
        class MemoriaFalsa:
            def get_context(self, tarea):
                return "[HISTORIAL previo]"

        estado = _build_agent_initial_state("tarea actual", memory=MemoriaFalsa())
        contenido = estado["messages"][0].content
        assert "[HISTORIAL previo]" in contenido
        assert "CURRENT TASK" in contenido
        assert "tarea actual" in contenido


class _GrafoFalso:
    """Graph fake: invoca el estado y devuelve un estado final."""

    def __init__(self, respuesta, estado_final=None):
        self.respuesta = respuesta
        self.estado_final = estado_final
        self.invocado_con = None

    def invoke(self, estado_inicial, config=None):
        self.invocado_con = estado_inicial
        if self.estado_final:
            return self.estado_final
        from langchain_core.messages import AIMessage
        return {"messages": [AIMessage(content=self.respuesta)], "status": "done"}


class _MemoriaFalsa:
    def __init__(self):
        self.guardadas = []
        self.facts = []

    def get_context(self, tarea):
        return None

    def add(self, tarea, resultado, agentes):
        self.guardadas.append((tarea, resultado, agentes))


class TestRun:
    def test_run_solo_devuelve_respuesta_del_grafo(self):
        memoria = _MemoriaFalsa()
        grafo = _GrafoFalso("respuesta final")
        resultado = run(
            task="tarea", solo=True, graph=grafo, memory=memoria,
            evaluator=None, logger=None,
        )
        assert resultado == "respuesta final"
        # La tarea exitosa se guarda en memoria
        assert memoria.guardadas[0][0] == "tarea"
        assert memoria.guardadas[0][2] == ["solo"]

    def test_run_planner_guarda_agentes_usados_del_plan(self):
        memoria = _MemoriaFalsa()
        grafo = _GrafoFalso(
            "resumen",
            estado_final={
                "messages": None,
                "status": "done",
                "plan": [{"agent": "coder", "subtask": "a"}, {"agent": "researcher", "subtask": "b"}],
            },
        )
        # run necesita messages en el estado final
        from langchain_core.messages import AIMessage
        grafo.estado_final["messages"] = [AIMessage(content="resumen")]
        resultado = run(
            task="tarea", solo=False, graph=grafo, memory=memoria,
            evaluator=None, logger=None,
        )
        assert resultado == "resumen"
        assert sorted(memoria.guardadas[0][2]) == ["coder", "researcher"]

    def test_run_no_guarda_respuestas_de_error_en_solo(self):
        memoria = _MemoriaFalsa()
        grafo = _GrafoFalso("Error: no se pudo completar")
        run(
            task="tarea", solo=True, graph=grafo, memory=memoria,
            evaluator=None, logger=None,
        )
        assert memoria.guardadas == []

    def test_run_no_guarda_fallos_estructurales_en_planner(self):
        from langchain_core.messages import AIMessage
        memoria = _MemoriaFalsa()
        grafo = _GrafoFalso(
            "algo",
            estado_final={
                "messages": [AIMessage(content="lo siento")],
                "status": "error",
                "plan": [],
            },
        )
        resultado = run(
            task="tarea", solo=False, graph=grafo, memory=memoria,
            evaluator=None, logger=None,
        )
        assert resultado == "lo siento"
        assert memoria.guardadas == []

    def test_run_sin_memoria_no_falla(self):
        grafo = _GrafoFalso("ok")
        resultado = run(
            task="tarea", solo=True, graph=grafo, memory=None,
            evaluator=None, logger=None,
        )
        assert resultado == "ok"
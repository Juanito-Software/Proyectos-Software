"""Tests de los estados definidos en core/state — contrato estructural."""
from core.state import AgentState, PlannerState


def test_agent_state_acepta_claves_esperadas():
    estado: AgentState = {
        "messages": [],
        "last_tool_result": None,
        "iteration": 0,
        "task": "tarea",
        "status": None,
        "error_count": 0,
    }
    assert estado["iteration"] == 0
    assert estado["task"] == "tarea"
    assert estado["status"] is None


def test_planner_state_acepta_claves_esperadas():
    estado: PlannerState = {
        "messages": [],
        "task": "tarea",
        "plan": [{"agent": "coder", "subtask": "x"}],
        "plan_step": 0,
        "results": [],
        "status": None,
        "iteration": 0,
    }
    assert estado["plan"][0]["agent"] == "coder"
    assert estado["plan_step"] == 0
    assert estado["results"] == []
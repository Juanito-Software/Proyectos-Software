"""
Estados del sistema — fuente única de verdad para LangGraph.
LangGraph es el ÚNICO responsable de mutar estos estados.
"""
from operator import add
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Estado de un agente especializado (hoja del árbol de agentes)."""
    messages: Annotated[list, add_messages]     # historial — append-only
    last_tool_result: Optional[str]
    iteration: int
    task: str
    status: Optional[str]
    error_count: int


class PlannerState(TypedDict):
    """Estado del Planner (raíz del árbol de agentes)."""
    messages: Annotated[list, add_messages]     # respuesta final al usuario
    task: str                                   # tarea original — inmutable
    plan: list[dict]                            # [{agent, subtask}, ...]
    plan_step: int                              # índice del paso en curso
    results: Annotated[list[str], add]          # resultados acumulados de cada agente
    status: Optional[str]
    iteration: int

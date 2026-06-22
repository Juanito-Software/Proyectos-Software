"""
OmniForge — punto de entrada.

Uso:
  python main.py "tu tarea"            # Planner multi-agente (por defecto)
  python main.py --solo "tu tarea"     # Agente único con todas las tools
  python main.py                       # Modo interactivo (Planner)
  python main.py --solo                # Modo interactivo (agente único)
"""
import sys
from langchain_core.messages import HumanMessage

from config import CONFIG


def _build_planner_initial_state(task: str) -> dict:
    return {
        "messages": [],
        "task": task,
        "plan": [],
        "plan_step": 0,
        "results": [],
        "status": None,
        "iteration": 0,
    }


def _build_agent_initial_state(task: str) -> dict:
    return {
        "messages": [HumanMessage(content=task)],
        "last_tool_result": None,
        "iteration": 0,
        "task": task,
        "status": None,
        "error_count": 0,
    }


def run(task: str, solo: bool = False) -> str:
    """Ejecuta una tarea y devuelve la respuesta final."""
    if solo:
        from core.graph import build_graph
        graph = build_graph(CONFIG)
        initial_state = _build_agent_initial_state(task)
    else:
        from core.planner import build_planner_graph
        graph = build_planner_graph(CONFIG)
        initial_state = _build_planner_initial_state(task)

    if CONFIG.agent.verbose:
        mode = "agente único" if solo else "planner multi-agente"
        print(f"\n[OmniForge] Tarea ({mode}): {task}\n{'─' * 60}")

    final_state = graph.invoke(initial_state)

    last_message = final_state["messages"][-1]
    response = getattr(last_message, "content", str(last_message))

    if CONFIG.agent.verbose:
        print(f"\n{'─' * 60}")

    return response


def interactive(solo: bool = False):
    """Bucle interactivo — escribe 'exit' para salir."""
    mode = "agente único" if solo else "planner multi-agente"
    print(f"OmniForge — modo interactivo ({mode}). Escribe 'exit' para salir.\n")

    while True:
        try:
            task = input("Tarea > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo.")
            break

        if task.lower() in ("exit", "quit", "q"):
            break

        if not task:
            continue

        result = run(task, solo=solo)
        print(f"\nRespuesta:\n{result}\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    solo = "--solo" in args
    task_parts = [a for a in args if a != "--solo"]

    if task_parts:
        task = " ".join(task_parts)
        result = run(task, solo=solo)
        print(result)
    else:
        interactive(solo=solo)

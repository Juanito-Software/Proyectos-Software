"""
OmniForge — punto de entrada.

Uso:
  python main.py "tu tarea"            # Planner multi-agente (por defecto)
  python main.py --solo "tu tarea"     # Agente único con todas las tools
  python main.py                       # Modo interactivo (Planner)
  python main.py --solo                # Modo interactivo (agente único)
"""
import os
import sys
import time
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from config import CONFIG


def _init_memory():
    """Crea y devuelve el MemoryStore si la memoria está habilitada, o None."""
    if not CONFIG.memory.enabled:
        return None
    from core.memory import MemoryStore
    return MemoryStore(
        path=CONFIG.memory.path,
        max_entries=CONFIG.memory.max_entries,
        max_context_chars=CONFIG.memory.max_context_chars,
        n_recent=CONFIG.memory.n_recent,
        max_facts=CONFIG.memory.max_facts,
        semantic_threshold=CONFIG.memory.semantic_threshold,
        embedding_model=CONFIG.memory.embedding_model,
        embedding_base_url=CONFIG.memory.embedding_base_url,
    )


def _init_logger():
    """Crea el OmniForgeLogger y configura LangSmith si procede. Devuelve None si disabled."""
    if not CONFIG.logging.enabled:
        return None
    from core.logger import OmniForgeLogger
    logger = OmniForgeLogger(CONFIG.logging.log_dir)
    if CONFIG.logging.langsmith_project and os.getenv("LANGCHAIN_API_KEY"):
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_PROJECT", CONFIG.logging.langsmith_project)
    return logger


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


def _build_agent_initial_state(task: str, memory=None) -> dict:
    content = task
    if memory:
        ctx = memory.get_context(task)
        if ctx:
            content = ctx + "\n\n---\nCurrent task: " + task
    return {
        "messages": [HumanMessage(content=content)],
        "last_tool_result": None,
        "iteration": 0,
        "task": task,
        "status": None,
        "error_count": 0,
    }


def run(task: str, solo: bool = False) -> str:
    """Ejecuta una tarea y devuelve la respuesta final."""
    memory = _init_memory()
    logger = _init_logger()
    mode = "solo" if solo else "planner"

    if logger:
        logger.session_start(task, mode)

    if CONFIG.agent.verbose:
        print(f"\n[OmniForge] Tarea ({mode}): {task}\n{'─' * 60}")

    if solo:
        from core.graph import build_graph
        graph = build_graph(CONFIG)
        initial_state = _build_agent_initial_state(task, memory)
    else:
        from core.planner import build_planner_graph
        graph = build_planner_graph(CONFIG, memory=memory)
        initial_state = _build_planner_initial_state(task)

    callbacks = [logger] if logger else []
    t0 = time.monotonic()
    final_state = graph.invoke(initial_state, config=RunnableConfig(callbacks=callbacks))
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    last_message = final_state["messages"][-1]
    response = getattr(last_message, "content", str(last_message))

    if logger:
        logger.session_end(response, elapsed_ms)

    if solo and memory:
        memory.add(task, response, ["solo"])
        if CONFIG.agent.verbose:
            print(f"[Memory] Tarea guardada. Total memorias: {len(memory)}")

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

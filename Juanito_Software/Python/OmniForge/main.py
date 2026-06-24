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


def _init_evaluator():
    if not CONFIG.evaluator.enabled:
        return None
    from core.evaluator import Evaluator
    return Evaluator(eval_dir=CONFIG.evaluator.eval_dir)


def _init_logger():
    if not CONFIG.logging.enabled:
        return None
    from core.logger import OmniForgeLogger
    logger = OmniForgeLogger(CONFIG.logging.log_dir)
    if CONFIG.logging.langsmith_project and os.getenv("LANGCHAIN_API_KEY"):
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_PROJECT", CONFIG.logging.langsmith_project)
    return logger


def _init_graph(solo: bool, memory, evaluator):
    """Construye el grafo una sola vez — es stateless, se reutiliza entre tareas."""
    if solo:
        from core.graph import build_graph
        return build_graph(CONFIG)
    else:
        from core.planner import build_planner_graph
        return build_planner_graph(CONFIG, memory=memory, evaluator=evaluator)


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
            content = (
                ctx
                + "\n\n════ CURRENT TASK (ignore history above, do THIS now) ════\n"
                + task
            )
    return {
        "messages": [HumanMessage(content=content)],
        "last_tool_result": None,
        "iteration": 0,
        "task": task,
        "status": None,
        "error_count": 0,
    }


def run(task: str, *, solo: bool, graph, memory, evaluator, logger) -> str:
    """
    Ejecuta una tarea y devuelve la respuesta final.
    Recibe los objetos ya inicializados — no los crea internamente.
    """
    mode = "solo" if solo else "planner"

    if logger:
        logger.session_start(task, mode)

    if CONFIG.agent.verbose:
        print(f"\n[OmniForge] Tarea ({mode}): {task}\n{'─' * 60}")

    initial_state = (
        _build_agent_initial_state(task, memory)
        if solo
        else _build_planner_initial_state(task)
    )

    callbacks = [logger] if logger else []
    t0 = time.monotonic()
    final_state = graph.invoke(initial_state, config=RunnableConfig(callbacks=callbacks))
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    msgs = final_state.get("messages", [])
    if not msgs:
        response = "Error: el agente no produjo respuesta."
    else:
        last_message = msgs[-1]
        response = getattr(last_message, "content", str(last_message)) or ""

    if logger:
        logger.session_end(response, elapsed_ms)

    if memory:
        # Solo guardar tareas exitosas — evita contaminar el historial con fallos.
        # En modo solo: éxito si la respuesta no es un mensaje de error.
        # En modo planner: éxito si synthesize() no marcó status="error".
        # Solo excluir fallos estructurales (timeout, plan vacío).
        # Errores de tool puntuales (wrong_agent, tool_errors) son recuperables:
        # el agente completó la tarea aunque con tropiezos — vale la pena recordarlo.
        fatal_failures = {"timeout", "plan_empty"}
        final_status = final_state.get("status", "done")
        task_succeeded = (
            not response.startswith("Error:")
            if solo
            else final_status not in fatal_failures
        )
        if task_succeeded:
            agents_used = (
                ["solo"] if solo
                else list({s["agent"] for s in final_state.get("plan", [])})
            )
            memory.add(task, response, agents_used)
            if CONFIG.agent.verbose:
                print(f"[Memory] Tarea guardada. Total: {len(memory)} tareas, {len(memory.facts)} hechos.")
        elif CONFIG.agent.verbose:
            print("[Memory] Tarea no guardada (fallo detectado).")

    if CONFIG.agent.verbose:
        print(f"\n{'─' * 60}")

    return response


def interactive(solo: bool = False):
    """
    Bucle interactivo — escribe 'exit' para salir.
    Memory, evaluator, logger y graph se inicializan UNA sola vez.
    """
    mode = "agente único" if solo else "planner multi-agente"
    print(f"OmniForge — modo interactivo ({mode}). Escribe 'exit' para salir.\n")

    memory = _init_memory()
    evaluator = _init_evaluator()
    logger = _init_logger()
    graph = _init_graph(solo, memory, evaluator)

    # Registrar skill names en el logger para que las identifique en consola
    if logger:
        from core.skills import load_skills
        skill_map = load_skills()
        if skill_map:
            skill_names = {t.name for tools in skill_map.values() for t in tools}
            logger.register_skills(skill_names)

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

        result = run(task, solo=solo, graph=graph, memory=memory,
                     evaluator=evaluator, logger=logger)
        print(f"\nRespuesta:\n{result}\n")


if __name__ == "__main__":
    args = sys.argv[1:]
    solo = "--solo" in args
    task_parts = [a for a in args if a != "--solo"]

    if task_parts:
        task = " ".join(task_parts)
        memory = _init_memory()
        evaluator = _init_evaluator()
        logger = _init_logger()
        graph = _init_graph(solo, memory, evaluator)
        if logger:
            from core.skills import load_skills
            skill_map = load_skills()
            if skill_map:
                skill_names = {t.name for tools in skill_map.values() for t in tools}
                logger.register_skills(skill_names)
        result = run(task, solo=solo, graph=graph, memory=memory,
                     evaluator=evaluator, logger=logger)
        print(result)
    else:
        interactive(solo=solo)
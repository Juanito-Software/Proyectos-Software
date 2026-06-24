"""
AgentCore — grafo LangGraph.
_build_agent_graph() es el constructor genérico que usan los agentes especializados.
build_graph()        es el wrapper que construye OmniForge con todas las tools.

Mejoras arquitectónicas aplicadas:
  - Provider fallback chain (Hermes): si el LLM primario falla, intenta el siguiente.
  - Sandwich compression (Hermes): comprime mensajes del medio preservando cabeza + cola.
  - Sequential tool node (propio): evita ejecución paralela de tools en Ollama.
"""
from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import RemoveMessage
from langgraph.prebuilt import ToolNode

from core.state import AgentState
from config import OmniForgeConfig


OMNIFORGE_PROMPT = """You are OmniForge, an autonomous agent that fully controls a PC.
Your capabilities:
- Execute code in Python, shell, JavaScript, and other languages
- Navigate the web via an automated browser
- Read, write, and manage files on the local filesystem
- Control the screen: take screenshots, click, type, press keys, scroll

Rules:
- Always use tools to act — never guess outputs, file contents, or screen state.
- After taking a screenshot, describe what you see before deciding what to do next.
- If a tool returns an error, analyze it and retry with a corrected approach (max {max_retries} retries).
- When the task is fully complete, respond with a concise summary and stop calling tools.
- Prefer targeted tool calls over broad ones.
- Do not explain what you are about to do — just do it.
"""

# Cuántas palabras aproximadas caben en un mensaje antes de comprimir el historial.
# 0 = sin compresión. Ajustar según el context window del modelo.
_COMPRESS_AFTER_MESSAGES = 40   # umbral: número de mensajes en el historial
_COMPRESS_PROTECT_TAIL = 6      # preservar siempre los últimos N mensajes


def _build_agent_graph(
    config: OmniForgeConfig,
    tools: list,
    system_prompt: str,
    required_action_tools: frozenset | None = None,
    sequential_tools: bool = False,
):
    """
    Constructor genérico — crea un CompiledGraph con las tools y el prompt dados.

    required_action_tools: el agente no puede declarar done hasta haber llamado
      al menos una de estas tools (anti-hallucination).
    sequential_tools: si True, usa un nodo secuencial propio en lugar de ToolNode
      para garantizar ejecución ordenada independientemente del provider.
    """
    from core.llm import build_llm, build_llm_list

    # ── LLM principal + fallbacks (Hermes pattern) ────────────────────────────
    llm_chain = build_llm_list(config)   # [primario, fallback1, fallback2, ...]
    llm = llm_chain[0]

    bind_kwargs = {}
    if sequential_tools and config.llm.provider.lower() != "ollama":
        bind_kwargs["parallel_tool_calls"] = False

    def _bind(base_llm):
        try:
            return base_llm.bind_tools(tools, **bind_kwargs)
        except TypeError:
            return base_llm.bind_tools(tools)

    llm_with_tools = _bind(llm)
    fallback_llms_with_tools = [_bind(fb) for fb in llm_chain[1:]]

    # ── Tool node ─────────────────────────────────────────────────────────────
    if sequential_tools:
        # ToolNode usa asyncio.gather — ejecución paralela que rompe pc_controller.
        # Este nodo ejecuta las tool_calls una por una en el orden indicado por el LLM.
        _tool_map = {t.name: t for t in tools}

        def tool_node(state: AgentState) -> dict:
            last = state["messages"][-1]
            results = []
            for tc in (getattr(last, "tool_calls", []) or []):
                fn = _tool_map.get(tc.get("name", ""))
                if fn is None:
                    content = f"ERROR: herramienta '{tc.get('name')}' no encontrada."
                else:
                    try:
                        content = str(fn.invoke(tc.get("args", {})))
                    except Exception as e:
                        content = f"ERROR en {tc.get('name')}: {e}"
                results.append(ToolMessage(
                    content=content,
                    tool_call_id=tc.get("id", ""),
                    name=tc.get("name", ""),
                ))
            return {"messages": results}
    else:
        tool_node = ToolNode(tools)

    system_message = SystemMessage(content=system_prompt)

    # ── Nodos ─────────────────────────────────────────────────────────────────

    def reason(state: AgentState) -> AgentState:
        nonlocal llm_with_tools
        messages_for_llm = [system_message] + list(state["messages"])

        # Hermes pattern: proba el LLM primario y luego cada fallback en orden.
        last_err: Exception | None = None
        for attempt in [llm_with_tools] + fallback_llms_with_tools:
            try:
                response: AIMessage = attempt.invoke(messages_for_llm)
                return {
                    "messages": [response],
                    "iteration": state["iteration"] + 1,
                    "last_tool_result": None,
                }
            except Exception as e:
                if "parallel_tool_calls" in str(e):
                    # Provider rechaza el param en runtime — reconstruir sin él y persistir
                    llm_with_tools = llm.bind_tools(tools)
                    try:
                        response = llm_with_tools.invoke(messages_for_llm)
                        return {
                            "messages": [response],
                            "iteration": state["iteration"] + 1,
                            "last_tool_result": None,
                        }
                    except Exception as e2:
                        last_err = e2
                        continue
                last_err = e
                continue  # probar siguiente fallback

        raise last_err  # todos los providers fallaron

    def compress(state: AgentState) -> dict:
        """
        Sandwich compression (Hermes pattern):
        preserva el primer mensaje (contexto de tarea) + los últimos N,
        y resume el bloque intermedio con el LLM más barato disponible.

        IMPORTANTE: AgentState.messages usa add_messages (append-only).
        Para eliminar mensajes usamos RemoveMessage(id=...) — LangGraph los borra
        antes de añadir los nuevos. La cabeza y la cola se conservan intactas;
        solo el bloque intermedio se reemplaza por el resumen.
        """
        msgs = list(state["messages"])
        if len(msgs) <= _COMPRESS_PROTECT_TAIL + 1:
            return {}

        middle = msgs[1:-_COMPRESS_PROTECT_TAIL]   # excluye head[0] y tail[-N:]

        if not middle:
            return {}

        middle_text = "\n".join(
            f"[{type(m).__name__}] {getattr(m, 'content', '')!s:.300}"
            for m in middle
        )
        summary_prompt = (
            "Summarize the following agent conversation steps into 3-5 bullet points. "
            "Keep key findings, tool results, and decisions. Be factual and brief.\n\n"
            + middle_text
        )
        try:
            summary_resp = llm.invoke([HumanMessage(content=summary_prompt)])
            summary_content = getattr(summary_resp, "content", str(summary_resp))
            summary_msg = HumanMessage(content=f"[COMPRESSED HISTORY]\n{summary_content}")
            # Eliminar mensajes intermedios por ID; el summary queda justo después de head.
            # add_messages procesa primero los RemoveMessage y luego hace append del summary.
            to_remove = [RemoveMessage(id=m.id) for m in middle if getattr(m, "id", None)]
            if not to_remove:
                return {}   # mensajes sin ID — compresión no posible
            return {"messages": to_remove + [summary_msg]}
        except Exception:
            return {}   # si falla la compresión, continuar sin ella

    def should_compress(state: AgentState) -> Literal["compress", "reason"]:
        if (
            _COMPRESS_AFTER_MESSAGES > 0
            and len(state["messages"]) > _COMPRESS_AFTER_MESSAGES
        ):
            return "compress"
        return "reason"

    def _action_tool_called(messages: list) -> bool:
        """True si alguna tool de acción real aparece en el historial de ToolMessages."""
        if not required_action_tools:
            return True
        for m in messages:
            if isinstance(m, ToolMessage) and getattr(m, "name", "") in required_action_tools:
                return True
        return False

    def route(state: AgentState) -> Literal["tools", "remind", "end"]:
        last = state["messages"][-1]
        if state["iteration"] >= config.agent.max_iterations:
            return "end"
        if state["error_count"] >= config.agent.max_retries:
            return "end"
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"

        # Agente respondió con solo texto — verificar si le falta llamar action tools.
        # Máximo 2 reminders para evitar bucles en tareas sin UI.
        if not _action_tool_called(state["messages"]) and state["error_count"] < 2:
            return "remind"

        return "end"

    def remind(state: AgentState) -> dict:
        """Corrige al agente cuando responde con texto sin haber completado la acción."""
        if required_action_tools and not _action_tool_called(state["messages"]):
            action_list = ", ".join(sorted(required_action_tools))
            content = (
                f"You responded with text but have NOT yet called any of the required action tools: "
                f"{action_list}. "
                "Setup tools (run_command, sleep_seconds, list_open_windows, take_screenshot) "
                "do NOT complete the task — they only prepare the environment. "
                "CRITICAL: The app is ALREADY OPEN — do NOT call run_command again, "
                "that would open a second instance. "
                "Go directly to step 5 (ACT): call click() to focus the text area, "
                "then call type_text() to type, or press_key() for key presses. "
                "Do NOT report completion without calling these tools first."
            )
        elif any(isinstance(m, ToolMessage) for m in state["messages"]):
            content = (
                "You responded with text but the task is NOT complete yet. "
                "You MUST now call the action tools: click(), type_text(), press_key(), etc. "
                "Proceed to step 5 (ACT) — do NOT report completion until you have performed "
                "the actual action and verified it with read_screen_text()."
            )
        else:
            content = (
                "You wrote text but did not call any tools. "
                "Writing text does NOT perform any action on the computer. "
                "You MUST call a tool RIGHT NOW. Start with run_command or take_screenshot."
            )
        return {"messages": [HumanMessage(content=content)], "error_count": state["error_count"] + 1}

    def handle_tool_error(state: AgentState) -> AgentState:
        messages = state["messages"]
        error_count = state["error_count"]
        last_content = getattr(messages[-1], "content", "") or ""

        n_tools = 0
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                n_tools = len(getattr(msg, "tool_calls", []) or [])
                break

        batch = messages[-n_tools:] if n_tools > 1 else [messages[-1]]
        for msg in batch:
            content = getattr(msg, "content", "") or ""
            if isinstance(content, str) and content.startswith("ERROR"):
                error_count += 1

        return {"last_tool_result": last_content, "error_count": error_count}

    # ── Construcción del grafo ─────────────────────────────────────────────────
    graph = StateGraph(AgentState)
    graph.add_node("reason", reason)
    graph.add_node("compress", compress)
    graph.add_node("tools", tool_node)
    graph.add_node("post_tools", handle_tool_error)
    graph.add_node("remind", remind)

    graph.set_entry_point("reason")
    graph.add_conditional_edges("reason", route, {
        "tools": "tools",
        "remind": "remind",
        "end": END,
    })
    graph.add_edge("tools", "post_tools")
    # Después de cada ciclo de tools: comprimir si el historial es largo
    graph.add_conditional_edges("post_tools", should_compress, {
        "compress": "compress",
        "reason": "reason",
    })
    graph.add_edge("compress", "reason")
    graph.add_edge("remind", "reason")
    return graph.compile()


def build_graph(config: OmniForgeConfig):
    """OmniForge completo — todas las tools, usado en modo --solo."""
    from tools import ALL_TOOLS
    return _build_agent_graph(
        config=config,
        tools=ALL_TOOLS,
        system_prompt=OMNIFORGE_PROMPT.format(max_retries=config.agent.max_retries),
    )
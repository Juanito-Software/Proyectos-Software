"""
AgentCore — grafo LangGraph.
_build_agent_graph() es el constructor genérico que usan los agentes especializados.
build_graph()        es el wrapper que construye OmniForge con todas las tools.
"""
from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
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
    sequential_tools: si True, pasa parallel_tool_calls=False al LLM para forzar
      una tool por respuesta. Necesario en pc_controller donde el orden importa
      (run_command debe completar antes de que click ocurra).
    """
    from core.llm import build_llm

    llm = build_llm(config)
    bind_kwargs = {}
    if sequential_tools:
        bind_kwargs["parallel_tool_calls"] = False
    try:
        llm_with_tools = llm.bind_tools(tools, **bind_kwargs)
    except TypeError:
        # El provider no soporta parallel_tool_calls → ignorar
        llm_with_tools = llm.bind_tools(tools)
    tool_node = ToolNode(tools)
    system_message = SystemMessage(content=system_prompt)

    def reason(state: AgentState) -> AgentState:
        messages_for_llm = [system_message] + list(state["messages"])
        response: AIMessage = llm_with_tools.invoke(messages_for_llm)
        return {
            "messages": [response],
            "iteration": state["iteration"] + 1,
            "last_tool_result": None,
        }

    def _action_tool_called(messages: list) -> bool:
        """True si alguna tool de acción real aparece en el historial de ToolMessages."""
        if not required_action_tools:
            return True  # sin restricción → siempre se considera que hay acción
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

        # Agente respondió con texto sin llamar tools.
        # Si requerimos tools de acción y ninguna se ha llamado → hallucination.
        # Máximo 2 reminders por sesión (error_count < 2) para evitar bucles
        # en tareas que genuinamente no necesitan acción UI.
        if not _action_tool_called(state["messages"]) and state["error_count"] < 2:
            return "remind"

        # Fallback genérico: early iterations con muy pocas tool calls → remind.
        tool_messages = [m for m in state["messages"] if isinstance(m, ToolMessage)]
        if len(tool_messages) < 3 and state["iteration"] < 4 and state["error_count"] < config.agent.max_retries:
            return "remind"

        return "end"

    def remind(state: AgentState) -> dict:
        """Injects a correction when the agent responded with text instead of tool calls."""
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

        # Find how many tool calls the preceding AIMessage batched together.
        # ToolNode appends one ToolMessage per call, so we check all of them,
        # not just the last one (which is the only one the old code checked).
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

    graph = StateGraph(AgentState)
    graph.add_node("reason", reason)
    graph.add_node("tools", tool_node)
    graph.add_node("post_tools", handle_tool_error)
    graph.add_node("remind", remind)
    graph.set_entry_point("reason")
    graph.add_conditional_edges("reason", route, {"tools": "tools", "remind": "remind", "end": END})
    graph.add_edge("tools", "post_tools")
    graph.add_edge("post_tools", "reason")
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

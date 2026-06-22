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


def _build_agent_graph(config: OmniForgeConfig, tools: list, system_prompt: str):
    """
    Constructor genérico — crea un CompiledGraph con las tools y el prompt dados.
    Cualquier agente especializado llama a esto en lugar de duplicar la lógica.
    """
    from core.llm import build_llm

    llm = build_llm(config)
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

    def route(state: AgentState) -> Literal["tools", "remind", "end"]:
        last = state["messages"][-1]
        if state["iteration"] >= config.agent.max_iterations:
            return "end"
        if state["error_count"] >= config.agent.max_retries:
            return "end"
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        # If no tool was ever called, the agent hallucinated — force a retry (max 3 times)
        any_tool_called = any(isinstance(m, ToolMessage) for m in state["messages"])
        if not any_tool_called and state["iteration"] < 3:
            return "remind"
        return "end"

    def remind(state: AgentState) -> dict:
        """Injects a correction when the agent responded with text instead of tool calls."""
        msg = HumanMessage(content=(
            "You wrote text but did not call any tools. "
            "Writing text does NOT perform any action on the computer. "
            "You MUST call a tool RIGHT NOW. Start with run_command or take_screenshot."
        ))
        return {"messages": [msg], "error_count": state["error_count"] + 1}

    def handle_tool_error(state: AgentState) -> AgentState:
        last = state["messages"][-1]
        content = getattr(last, "content", "") or ""
        error_count = state["error_count"]
        if isinstance(content, str) and content.startswith("ERROR"):
            error_count += 1
        return {"last_tool_result": content, "error_count": error_count}

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

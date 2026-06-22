"""
Planner — orquestador multi-agente.

Flujo:
  [plan] → genera lista de pasos {agent, subtask}
     ↓
  [execute_step] → invoca el agente especializado del paso actual
     ↓  (repite hasta completar todos los pasos)
  [synthesize] → combina resultados en una respuesta final
"""
import json
import re
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from core.state import AgentState, PlannerState
from core.agents import REGISTRY, build_agent
from config import OmniForgeConfig


# ── Prompts ──────────────────────────────────────────────────────────────────

def _planner_prompt(agent_list: str) -> str:
    return f"""You are the OmniForge Planner. You orchestrate specialized AI agents to complete tasks.

Available agents:
{agent_list}

Analyze the user's task and break it into subtasks.
Return ONLY a valid JSON array — no explanation, no markdown fences:
[{{"agent": "<name>", "subtask": "<what to do>"}}, ...]

Rules:
- Use the MINIMUM steps needed. Fewer steps is always better.
- CRITICAL: If multiple consecutive actions belong to the same agent, merge them into ONE step.
  Example: "open notepad and type hello" → single pc_controller step, NOT two steps.
- Only split into separate steps when a DIFFERENT agent is needed, or when step B truly cannot
  start until step A's output is known.
- Only include agents that are actually required.
- Be specific in subtasks — each agent only sees its own subtask, not the full context.
- If step B needs the output of step A, say so explicitly in step B's subtask.
"""


def _synthesizer_prompt(task: str, results: list[str]) -> str:
    results_block = "\n\n".join(results)
    return f"""You completed a multi-agent task. Write a clear, concise summary for the user.

Original task: {task}

Agent results:
{results_block}

Respond directly — no headers, no bullet points unless they help clarity.
"""


# ── Plan parsing ──────────────────────────────────────────────────────────────

def _parse_plan(text: str) -> list[dict]:
    """Extrae el JSON del plan desde el texto del LLM. Robusto a texto adicional."""
    match = re.search(r'\[.*?\]', text, re.DOTALL)
    if not match:
        return []
    try:
        steps = json.loads(match.group())
        valid = [s for s in steps if isinstance(s, dict) and "agent" in s and "subtask" in s]
        return valid
    except json.JSONDecodeError:
        return []


# ── Grafo ─────────────────────────────────────────────────────────────────────

def build_planner_graph(config: OmniForgeConfig):
    """
    Construye y compila el Planner.
    Devuelve un CompiledGraph que acepta PlannerState.
    """
    from core.llm import build_llm

    llm = build_llm(config)

    # Construir agentes una sola vez — son costosos de inicializar
    specialized_agents = {name: build_agent(name, config) for name in REGISTRY}

    agent_list_text = "\n".join(
        f"- {name}: {entry['description']}" for name, entry in REGISTRY.items()
    )
    planner_system = SystemMessage(content=_planner_prompt(agent_list_text))

    # ── Nodos ─────────────────────────────────────────────────────────────────

    def plan(state: PlannerState) -> dict:
        """El LLM analiza la tarea y devuelve el plan estructurado."""
        if config.agent.verbose:
            print(f"\n[Planner] Planificando: {state['task']}")

        response: AIMessage = llm.invoke(
            [planner_system, HumanMessage(content=state["task"])]
        )
        steps = _parse_plan(response.content)

        if not steps:
            # Fallback: si el LLM no devuelve JSON válido, tarea completa al coder
            steps = [{"agent": "coder", "subtask": state["task"]}]

        if config.agent.verbose:
            for i, s in enumerate(steps, 1):
                print(f"  {i}. [{s['agent']}] {s['subtask']}")

        return {
            "plan": steps,
            "plan_step": 0,
            "iteration": state["iteration"] + 1,
        }

    def execute_step(state: PlannerState) -> dict:
        """Invoca el agente del paso actual y recoge su resultado."""
        idx = state["plan_step"]
        step = state["plan"][idx]
        agent_name = step["agent"]
        subtask = step["subtask"]

        if config.agent.verbose:
            total = len(state["plan"])
            print(f"\n[Planner] Paso {idx + 1}/{total} → [{agent_name}]")
            print(f"  Subtarea: {subtask}")

        if agent_name not in specialized_agents:
            result = f"ERROR: agente '{agent_name}' no registrado. Disponibles: {list(REGISTRY)}"
        else:
            agent = specialized_agents[agent_name]
            # Prepend prior results so the agent has full context of what was done before
            prior = state["results"]
            if prior:
                context_prefix = "Context from previous steps:\n" + "\n".join(prior) + "\n\n"
                full_subtask = context_prefix + "Your task: " + subtask
            else:
                full_subtask = subtask
            agent_initial_state: AgentState = {
                "messages": [HumanMessage(content=full_subtask)],
                "last_tool_result": None,
                "iteration": 0,
                "task": full_subtask,
                "status": None,
                "error_count": 0,
            }
            try:
                final_agent_state = agent.invoke(agent_initial_state)
                last_msg = final_agent_state["messages"][-1]
                result = getattr(last_msg, "content", str(last_msg))
            except Exception as e:
                result = f"ERROR en {agent_name}: {e}"

        if config.agent.verbose:
            preview = result[:200] + "…" if len(result) > 200 else result
            print(f"  Resultado: {preview}")

        return {
            "results": [f"[{agent_name}] paso {idx + 1}: {result}"],
            "plan_step": idx + 1,
        }

    def synthesize(state: PlannerState) -> dict:
        """Sintetiza todos los resultados en la respuesta final al usuario."""
        if config.agent.verbose:
            print("\n[Planner] Sintetizando respuesta final…")

        prompt = _synthesizer_prompt(state["task"], state["results"])
        response: AIMessage = llm.invoke([HumanMessage(content=prompt)])
        return {"messages": [response], "status": "done"}

    # ── Condiciones de routing ─────────────────────────────────────────────────

    def after_plan(state: PlannerState) -> Literal["execute_step", "__end__"]:
        return "execute_step" if state.get("plan") else "__end__"

    def after_step(state: PlannerState) -> Literal["execute_step", "synthesize"]:
        if state["plan_step"] >= len(state["plan"]):
            return "synthesize"
        return "execute_step"

    # ── Construcción del grafo ─────────────────────────────────────────────────

    graph = StateGraph(PlannerState)

    graph.add_node("plan", plan)
    graph.add_node("execute_step", execute_step)
    graph.add_node("synthesize", synthesize)

    graph.set_entry_point("plan")
    graph.add_conditional_edges("plan", after_plan,
                                {"execute_step": "execute_step", "__end__": END})
    graph.add_conditional_edges("execute_step", after_step,
                                {"execute_step": "execute_step", "synthesize": "synthesize"})
    graph.add_edge("synthesize", END)

    return graph.compile()

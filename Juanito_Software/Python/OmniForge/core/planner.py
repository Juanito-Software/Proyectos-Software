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

Tool-to-agent mapping (STRICT — never assign a tool to the wrong agent):
- describe_screen   → ALWAYS pc_controller
- find_element      → ALWAYS pc_controller
- read_screen_text  → coder OR pc_controller
- find_text_on_screen → coder OR pc_controller
- take_screenshot / click / type / keyboard → pc_controller
- run_code / run_command / read_file / write_file → coder
- web_search / browse_url → researcher

If the user explicitly names a tool (e.g. "use describe_screen"), assign the task to the agent
that owns that tool — do NOT substitute a different tool.
"""


def _synthesizer_prompt(task: str, results: list[str]) -> str:
    results_block = "\n\n".join(results)
    return f"""You completed a multi-agent task. Write a clear, concise summary for the user.

Original task: {task}

Agent results:
{results_block}

Respond directly — no headers, no bullet points unless they help clarity.
"""


def _fact_extractor_prompt(task: str, result: str) -> str:
    return f"""A task was just completed. Extract 0-3 short facts worth remembering for future sessions.

Rules:
- Facts must be SPECIFIC and DURABLE: file paths, installed apps, user habits, system config.
- Skip task-specific details that won't help future tasks.
- If there is nothing worth remembering, return [].
- Return ONLY a valid JSON array of strings: ["fact 1", "fact 2"] or []

Task: {task[:300]}
Result: {result[:500]}"""


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

def build_planner_graph(config: OmniForgeConfig, memory=None, evaluator=None):
    """
    Construye y compila el Planner.
    memory:    MemoryStore opcional — contexto histórico + hechos.
    evaluator: Evaluator opcional  — evalúa cada tarea y genera hints de mejora.
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

        task_content = state["task"]
        if memory:
            ctx = memory.get_context(state["task"])
            if ctx:
                task_content = ctx + "\n\n---\nCurrent task: " + task_content
                if config.agent.verbose:
                    mode = "semántica" if len(memory) > config.memory.semantic_threshold else "cronológica"
                    print(f"[Memory] {len(memory)} tareas, recuperación {mode}.")

        response: AIMessage = llm.invoke(
            [planner_system, HumanMessage(content=task_content)]
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

        if memory:
            agents_used = list({s["agent"] for s in state["plan"]})
            memory.add(state["task"], response.content, agents_used)
            if config.agent.verbose:
                print(f"[Memory] Tarea guardada. Total: {len(memory)} tareas, {len(memory.facts)} hechos.")

            if config.memory.extract_facts:
                try:
                    extract_resp: AIMessage = llm.invoke(
                        [HumanMessage(content=_fact_extractor_prompt(state["task"], response.content))]
                    )
                    match = re.search(r'\[.*?\]', extract_resp.content, re.DOTALL)
                    if match:
                        raw_facts = json.loads(match.group())
                        added = [f for f in raw_facts if isinstance(f, str) and memory.add_fact(f)]
                        if added and config.agent.verbose:
                            for f in added:
                                print(f"  [Fact] {f}")
                except Exception:
                    pass  # extracción de hechos nunca interrumpe el flujo principal

        if evaluator:
            try:
                ev = evaluator.evaluate(
                    task=state["task"],
                    plan=state["plan"],
                    results=state["results"],
                    iterations=state["iteration"],
                    max_iterations=config.agent.max_iterations,
                )
                evaluator.save(ev)
                if config.agent.verbose:
                    status = ev.failure_type or "ok"
                    print(f"[Eval] efficiency={ev.efficiency} failure={status}")

                if evaluator.should_analyze():
                    hint = evaluator.analyze_and_generate_hint(llm)
                    if hint and memory:
                        added = memory.add_fact(f"[HINT] {hint}")
                        if added and config.agent.verbose:
                            print(f"[Eval] Nuevo hint de planificación: {hint}")
            except Exception:
                pass  # la evaluación nunca interrumpe el flujo principal

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

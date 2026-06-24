"""
Nivel 3 — capa de observación, evaluación y mejora.

Flujo por tarea:
  synthesize() → evaluate() → save() → [cada N tareas] analyze_and_generate_hint()
                                              ↓
                                     hint guardado en memory como [HINT] fact
                                              ↓
                              plan() lo lee automáticamente en el siguiente run

Archivos en disco:
  evaluations.jsonl  — una TaskEvaluation por línea, append-only
"""
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── Clasificación de fallos ────────────────────────────────────────────────────

FAILURE_NONE = None
FAILURE_TIMEOUT = "timeout"           # iterations >= max_iterations
FAILURE_TOOL_ERRORS = "tool_errors"   # múltiples ERRORs en resultados
FAILURE_WRONG_AGENT = "wrong_agent"   # ERROR + un solo agente → mala asignación
FAILURE_PLAN_EMPTY = "plan_empty"     # plan con 0 pasos (fallback activado)


# ── Dataclass de evaluación ───────────────────────────────────────────────────

@dataclass
class TaskEvaluation:
    id: str
    timestamp: str
    task: str               # truncado a 200 chars para el JSONL
    plan_steps: int
    iterations: int
    max_iterations: int
    error_count: int        # ERRORs en resultados de agentes
    agents_used: list[str]
    failure_type: Optional[str]
    efficiency: float       # 0.0 (pésimo) – 1.0 (perfecto)


# ── Evaluador ─────────────────────────────────────────────────────────────────

class Evaluator:
    """
    Registra, evalúa y analiza ejecuciones del Planner.
    analyze_and_generate_hint() usa el LLM para detectar patrones sistémicos
    y producir hints de planificación que se almacenan en MemoryStore.
    """

    def __init__(self, eval_dir: str, analyze_every: int = 10) -> None:
        self._path = Path(eval_dir) / "evaluations.jsonl"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self.analyze_every = analyze_every
        self._count = self._count_existing()

    def _count_existing(self) -> int:
        if not self._path.exists():
            return 0
        try:
            return sum(1 for line in self._path.open(encoding="utf-8") if line.strip())
        except OSError:
            return 0

    # ── Evaluación ────────────────────────────────────────────────────────────

    def evaluate(
        self,
        task: str,
        plan: list[dict],
        results: list[str],
        iterations: int,
        max_iterations: int,
    ) -> TaskEvaluation:
        agents_used = list({s["agent"] for s in plan})
        # Los resultados tienen formato "[agent] paso N: <contenido>"
        error_results = [r for r in results if "ERROR" in r]
        error_count = len(error_results)

        # Clasificar tipo de fallo
        if not plan:
            failure = FAILURE_PLAN_EMPTY
        elif iterations >= max_iterations:
            failure = FAILURE_TIMEOUT
        elif error_count >= 2:
            failure = FAILURE_TOOL_ERRORS
        elif error_count == 1 and len(agents_used) == 1:
            failure = FAILURE_WRONG_AGENT
        else:
            failure = FAILURE_NONE

        # Score de eficiencia
        iter_ratio = iterations / max(max_iterations, 1)
        error_penalty = min(error_count * 0.2, 0.4)
        efficiency = round(max(0.0, 1.0 - iter_ratio * 0.6 - error_penalty), 2)

        return TaskEvaluation(
            id=datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:18],
            timestamp=datetime.now().isoformat(timespec="seconds"),
            task=task[:200],
            plan_steps=len(plan),
            iterations=iterations,
            max_iterations=max_iterations,
            error_count=error_count,
            agents_used=agents_used,
            failure_type=failure,
            efficiency=efficiency,
        )

    def save(self, ev: TaskEvaluation) -> None:
        try:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(ev), ensure_ascii=False) + "\n")
            self._count += 1
        except OSError:
            pass

    def should_analyze(self) -> bool:
        return self._count > 0 and self._count % self.analyze_every == 0

    # ── Análisis de patrones ──────────────────────────────────────────────────

    def load_recent(self, n: int = 30) -> list[dict]:
        if not self._path.exists():
            return []
        try:
            lines = self._path.read_text(encoding="utf-8").splitlines()
            return [json.loads(l) for l in lines[-n:] if l.strip()]
        except (OSError, json.JSONDecodeError):
            return []

    def _format_for_analysis(self, evaluations: list[dict]) -> str:
        lines = []
        for e in evaluations:
            fail = e["failure_type"] or "ok"
            lines.append(
                f"task={e['task'][:80]!r} | "
                f"agents={e['agents_used']} | "
                f"steps={e['plan_steps']} | "
                f"iters={e['iterations']}/{e['max_iterations']} | "
                f"errors={e['error_count']} | "
                f"fail={fail} | "
                f"eff={e['efficiency']}"
            )
        return "\n".join(lines)

    def analyze_and_generate_hint(self, llm) -> Optional[str]:
        """
        Analiza las últimas evaluaciones y genera un hint de planificación si detecta
        un patrón sistémico. Devuelve el hint como string, o None si no hay patrón claro.

        El hint se almacena en MemoryStore como fact con prefijo [HINT] y se inyecta
        automáticamente al Planner en el siguiente plan().
        """
        recent = self.load_recent(30)
        if len(recent) < 5:
            return None

        from langchain_core.messages import HumanMessage

        prompt = f"""You are analyzing execution logs of a multi-agent AI planner. Identify ONE systemic pattern causing repeated failures or inefficiency.

Recent task evaluations (chronological):
{self._format_for_analysis(recent)}

Failure types: timeout=too many iterations, tool_errors=multiple agent errors,
               wrong_agent=error with single agent (bad routing), plan_empty=JSON parse fail, ok=success

Rules for your response:
- Only report a pattern if it appears in AT LEAST 3 of the last 10 evaluations.
- The hint must be a concrete, actionable planning rule (not a vague observation).
- Max 120 characters.
- If no clear pattern: respond NO_PATTERN

Respond with EXACTLY one of:
HINT: <actionable rule for the planner>
NO_PATTERN"""

        try:
            response = llm.invoke([HumanMessage(content=prompt)])
            text = response.content.strip()
            if text.startswith("HINT:"):
                return text[5:].strip()[:120]
        except Exception:
            pass
        return None

    def summary(self) -> dict:
        """Estadísticas rápidas del histórico de evaluaciones."""
        recent = self.load_recent(100)
        if not recent:
            return {"total": 0}
        efficiencies = [e["efficiency"] for e in recent]
        failures = [e["failure_type"] for e in recent if e["failure_type"]]
        return {
            "total": self._count,
            "avg_efficiency": round(sum(efficiencies) / len(efficiencies), 2),
            "failure_rate": round(len(failures) / len(recent), 2),
            "failure_breakdown": {
                ft: failures.count(ft) for ft in set(failures)
            },
        }

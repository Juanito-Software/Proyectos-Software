"""
Observabilidad estructurada — escribe eventos JSONL a ~/.omniforge/logs/YYYY-MM-DD.jsonl.
Implementado como LangChain callback: se propaga automáticamente por todo el grafo.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler


class OmniForgeLogger(BaseCallbackHandler):
    """
    Registra tool calls, LLM calls, errores y tiempos en formato JSONL.
    Pasar como callback en graph.invoke(state, config={"callbacks": [logger]}).
    """

    raise_error = False  # nunca interrumpir el agente por un fallo de logging

    def __init__(self, log_dir: str) -> None:
        super().__init__()
        self._dir = Path(log_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._file = self._dir / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self._tool_t: dict[str, float] = {}
        self._llm_t: dict[str, float] = {}

    # ── I/O ───────────────────────────────────────────────────────────────────

    def _w(self, event: dict) -> None:
        event["ts"] = datetime.now().isoformat(timespec="milliseconds")
        try:
            with self._file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
        except OSError:
            pass  # logging nunca rompe el agente

    # ── API pública (eventos de sesión) ───────────────────────────────────────

    def session_start(self, task: str, mode: str) -> None:
        self._w({"event": "session_start", "task": task[:300], "mode": mode})

    def session_end(self, result: str, elapsed_ms: int) -> None:
        self._w({"event": "session_end", "result": result[:500], "elapsed_ms": elapsed_ms})

    def planner_step(self, step_idx: int, agent: str, subtask: str) -> None:
        self._w({"event": "planner_step", "step": step_idx, "agent": agent, "subtask": subtask[:200]})

    # ── LangChain hooks — tools ───────────────────────────────────────────────

    def on_tool_start(
        self, serialized: dict, input_str: str, *, run_id: UUID, **kwargs: Any
    ) -> None:
        name = serialized.get("name", "unknown_tool")
        self._tool_t[str(run_id)] = time.monotonic()
        self._w({"event": "tool_call", "tool": name, "input": str(input_str)[:300]})

    def on_tool_end(self, output: Any, *, run_id: UUID, **kwargs: Any) -> None:
        elapsed = time.monotonic() - self._tool_t.pop(str(run_id), time.monotonic())
        self._w({
            "event": "tool_result",
            "output": str(output)[:500],
            "elapsed_ms": int(elapsed * 1000),
        })

    def on_tool_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        self._tool_t.pop(str(run_id), None)
        self._w({"event": "tool_error", "error": str(error)[:300]})

    # ── LangChain hooks — LLM (chat models) ──────────────────────────────────

    def on_chat_model_start(
        self, serialized: dict, messages: list, *, run_id: UUID, **kwargs: Any
    ) -> None:
        self._llm_t[str(run_id)] = time.monotonic()
        model = (
            serialized.get("kwargs", {}).get("model")
            or serialized.get("kwargs", {}).get("model_name")
            or serialized.get("name", "?")
        )
        n_msgs = sum(len(batch) for batch in messages)
        self._w({"event": "llm_call", "model": model, "n_messages": n_msgs})

    def on_llm_end(self, response: Any, *, run_id: UUID, **kwargs: Any) -> None:
        elapsed = time.monotonic() - self._llm_t.pop(str(run_id), time.monotonic())
        usage: dict = {}
        try:
            info = response.generations[0][0].generation_info or {}
            for key in ("input_tokens", "output_tokens", "prompt_tokens", "completion_tokens"):
                if key in info:
                    usage[key] = info[key]
        except Exception:
            pass
        self._w({"event": "llm_response", "elapsed_ms": int(elapsed * 1000), **usage})

    def on_llm_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        self._llm_t.pop(str(run_id), None)
        msg = str(error) or repr(error)  # algunos errores de Ollama tienen str() vacío
        self._w({"event": "llm_error", "error_type": type(error).__name__, "error": msg[:300]})

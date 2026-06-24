"""
Memoria persistente — tareas completadas, hechos durables y hints de planificación.

Recuperación adaptativa:
  ≤ semantic_threshold tareas → últimas n_recent en orden cronológico
  > semantic_threshold tareas → similitud coseno vía Ollama (nomic-embed-text)
                                Requiere: ollama pull nomic-embed-text
                                Si Ollama no está disponible, cae a cronológico.

Archivos en disco:
  memory.json            {"tasks": [...], "facts": [...], "hints": [...]}
  memory.embeddings.json {task_id: [float, ...]}   ← solo se crea al activar semántica

Separación facts/hints (P4):
  _facts  — hechos del usuario/sistema (file paths, apps instaladas, preferencias)
  _hints  — reglas de planificación generadas por el evaluador
  Deduplicación independiente: un hint nunca bloquea un fact con texto similar y viceversa.
"""
import json
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


class MemoryStore:
    def __init__(
        self,
        path: str,
        max_entries: int = 200,
        max_context_chars: int = 2000,
        n_recent: int = 8,
        max_facts: int = 50,
        semantic_threshold: int = 500,
        embedding_model: str = "nomic-embed-text",
        embedding_base_url: str = "http://localhost:11434",
    ) -> None:
        self.path = Path(path)
        self.max_entries = max_entries
        self.max_context_chars = max_context_chars
        self.n_recent = n_recent
        self.max_facts = max_facts
        self.semantic_threshold = semantic_threshold
        self.embedding_model = embedding_model
        self.embedding_base_url = embedding_base_url

        self._tasks: list[dict] = []
        self._facts: list[str] = []
        self._hints: list[str] = []          # P4: separado de _facts
        self._embeddings: dict[str, list[float]] = {}
        self._embed_path = self.path.with_name(self.path.stem + ".embeddings.json")
        self._embedder = None
        self._lock = threading.Lock()        # P6: protege _save() de escrituras concurrentes
        self._load()

    # ── Persistencia ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                self._tasks = data
                self._facts = []
                self._hints = []
            else:
                self._tasks = data.get("tasks", [])
                # Migración automática: separar [HINT] que vivían mezclados con facts
                raw_facts = data.get("facts", [])
                self._hints = data.get("hints", [])
                if not self._hints:
                    # Primera carga post-P4: extraer hints de la lista de facts antigua
                    self._hints = [f.replace("[HINT] ", "", 1) for f in raw_facts
                                   if f.startswith("[HINT]")]
                    raw_facts = [f for f in raw_facts if not f.startswith("[HINT]")]
                self._facts = raw_facts
        except (json.JSONDecodeError, OSError):
            pass

        if self._embed_path.exists():
            try:
                self._embeddings = json.loads(self._embed_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._embeddings = {}

    def _save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(
                    {"tasks": self._tasks, "facts": self._facts, "hints": self._hints},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

    def _save_embeddings(self) -> None:
        try:
            self._embed_path.write_text(
                json.dumps(self._embeddings, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            pass

    # ── Embeddings (Ollama) ───────────────────────────────────────────────────

    def _get_embedder(self):
        if self._embedder is None:
            from langchain_ollama import OllamaEmbeddings
            self._embedder = OllamaEmbeddings(
                model=self.embedding_model,
                base_url=self.embedding_base_url,
            )
        return self._embedder

    def _embed(self, text: str) -> list[float]:
        return self._get_embedder().embed_query(text)

    def _backfill_embeddings(self) -> None:
        missing = [t for t in self._tasks if t["id"] not in self._embeddings]
        if not missing:
            return
        for task in missing:
            self._embeddings[task["id"]] = self._embed(task["task"])
        self._save_embeddings()

    # ── API — tareas ──────────────────────────────────────────────────────────

    def add(self, task: str, result: str, agents_used: list[str] | None = None) -> None:
        entry = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "task": task,
            "result": result,
            "agents_used": agents_used or [],
        }
        self._tasks.append(entry)
        if len(self._tasks) > self.max_entries:
            self._tasks = self._tasks[-self.max_entries:]
        self._save()

        warmup_start = max(1, self.semantic_threshold - 100)
        if len(self._tasks) >= warmup_start:
            try:
                if entry["id"] not in self._embeddings:
                    self._embeddings[entry["id"]] = self._embed(entry["task"])
                    self._save_embeddings()
            except Exception:
                pass

    # ── API — hechos de usuario ───────────────────────────────────────────────

    def add_fact(self, fact: str, _save: bool = True) -> bool:
        """Añade un hecho de usuario si no es redundante. Deduplicación solo contra _facts."""
        fact = fact.strip()
        if not fact:
            return False
        fl = fact.lower()
        for existing in self._facts:
            if fl in existing.lower() or existing.lower() in fl:
                return False
        self._facts.append(fact)
        if len(self._facts) > self.max_facts:
            self._facts = self._facts[-self.max_facts:]
        if _save:
            self._save()
        return True

    def add_facts(self, facts: list[str]) -> list[str]:
        """Añade múltiples hechos con una sola escritura a disco."""
        added = [f for f in facts if self.add_fact(f, _save=False)]
        if added:
            self._save()
        return added

    @property
    def facts(self) -> list[str]:
        return list(self._facts)

    # ── API — hints del evaluador ─────────────────────────────────────────────

    def add_hint(self, hint: str) -> bool:
        """
        Añade un hint de planificación generado por el evaluador.
        Deduplicación independiente de _facts — un hint nunca bloquea un fact.
        """
        hint = hint.strip()
        if not hint:
            return False
        hl = hint.lower()
        for existing in self._hints:
            if hl in existing.lower() or existing.lower() in hl:
                return False
        self._hints.append(hint)
        if len(self._hints) > self.max_facts:   # mismo límite que facts
            self._hints = self._hints[-self.max_facts:]
        self._save()
        return True

    @property
    def hints(self) -> list[str]:
        return list(self._hints)

    # ── Búsqueda semántica ────────────────────────────────────────────────────

    def _semantic_search(self, query: str, top_k: int) -> list[dict]:
        import numpy as np

        self._backfill_embeddings()
        candidates = [t for t in self._tasks if t["id"] in self._embeddings]
        if not candidates:
            return self._tasks[-top_k:]

        q_vec = np.array(self._embed(query), dtype=np.float32)
        matrix = np.array(
            [self._embeddings[t["id"]] for t in candidates], dtype=np.float32
        )

        q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-8)
        m_norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8
        scores = (matrix / m_norms) @ q_norm

        k = min(top_k, len(candidates))
        top_idx = np.argpartition(scores, -k)[-k:]
        selected_ids = {candidates[i]["id"] for i in top_idx}
        return [t for t in self._tasks if t["id"] in selected_ids]

    # ── Contexto para el LLM ──────────────────────────────────────────────────

    def get_context(self, query: str = None) -> Optional[str]:
        parts: list[str] = []

        # Hints del evaluador — reglas de planificación, sección propia
        if self._hints:
            parts.append(
                "[PLANNING HINTS — rules derived from past failures, follow these]\n"
                + "\n".join(f"• {h}" for h in self._hints)
            )

        # Hechos del usuario/sistema
        if self._facts:
            parts.append(
                "[SYSTEM FACTS — use these to inform decisions]\n"
                + "\n".join(f"• {f}" for f in self._facts)
            )

        # Tareas pasadas
        if self._tasks:
            use_semantic = query is not None and len(self._tasks) > self.semantic_threshold
            header = "[PAST SESSION LOG — completed tasks, shown for context only. Do NOT re-execute these.]"

            if use_semantic:
                try:
                    recent = self._semantic_search(query, top_k=self.n_recent)
                    header = "[RELEVANT PAST SESSION LOG — for context only. Do NOT re-execute these.]"
                except Exception:
                    recent = self._tasks[-self.n_recent:]
            else:
                recent = self._tasks[-self.n_recent:]

            lines = []
            for e in recent:
                ts = e["timestamp"][:16].replace("T", " ")
                agents = ", ".join(e["agents_used"]) if e["agents_used"] else "?"
                lines.append(
                    f"• [{ts}] ({agents}) previously completed: {e['task'][:120]}\n"
                    f"  outcome: {e['result'][:200]}"
                )
            parts.append(header + "\n" + "\n".join(lines))

        if not parts:
            return None

        return "\n\n".join(parts)[:self.max_context_chars]

    def __len__(self) -> int:
        return len(self._tasks)
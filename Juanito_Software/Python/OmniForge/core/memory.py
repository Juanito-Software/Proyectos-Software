"""
Memoria persistente — tareas completadas y hechos durables entre sesiones.

Recuperación adaptativa:
  ≤ semantic_threshold tareas → últimas n_recent en orden cronológico
  > semantic_threshold tareas → similitud coseno vía Ollama (nomic-embed-text)
                                Requiere: ollama pull nomic-embed-text
                                Si Ollama no está disponible, cae a cronológico.

Archivos en disco:
  memory.json            {"tasks": [...], "facts": [...]}
  memory.embeddings.json {task_id: [float, ...]}   ← solo se crea al activar semántica
"""
import json
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
        self._embeddings: dict[str, list[float]] = {}
        self._embed_path = self.path.with_name(self.path.stem + ".embeddings.json")
        self._embedder = None  # lazy — solo se inicializa al superar el umbral
        self._load()

    # ── Persistencia ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, list):           # backward compat: formato antiguo
                self._tasks = data
                self._facts = []
            else:
                self._tasks = data.get("tasks", [])
                self._facts = data.get("facts", [])
        except (json.JSONDecodeError, OSError):
            pass

        if self._embed_path.exists():
            try:
                self._embeddings = json.loads(self._embed_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._embeddings = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {"tasks": self._tasks, "facts": self._facts},
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
        """
        Computa embeddings para tareas sin vector (primera vez que se activa semántica,
        o tareas cargadas de disco antes de que se calculase el umbral).
        Coste one-time: ~30ms/tarea en CPU.
        """
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
            self._tasks = self._tasks[-self.max_entries :]
        self._save()

        # Precalentar embeddings en el tramo previo al umbral para que la
        # primera búsqueda semántica no imponga una pausa larga al usuario.
        warmup_start = max(1, self.semantic_threshold - 100)
        if len(self._tasks) >= warmup_start:
            try:
                if entry["id"] not in self._embeddings:
                    self._embeddings[entry["id"]] = self._embed(entry["task"])
                    self._save_embeddings()
            except Exception:
                pass  # Ollama no disponible — modo cronológico como fallback

    # ── API — hechos ──────────────────────────────────────────────────────────

    def add_fact(self, fact: str) -> bool:
        """
        Añade un hecho si no es redundante (deduplicación por substring).
        Devuelve True si fue añadido.
        """
        fact = fact.strip()
        if not fact:
            return False
        fl = fact.lower()
        for existing in self._facts:
            el = existing.lower()
            if fl in el or el in fl:
                return False
        self._facts.append(fact)
        if len(self._facts) > self.max_facts:
            self._facts = self._facts[-self.max_facts :]
        self._save()
        return True

    @property
    def facts(self) -> list[str]:
        return list(self._facts)

    # ── Búsqueda semántica ────────────────────────────────────────────────────

    def _semantic_search(self, query: str, top_k: int) -> list[dict]:
        """
        Similitud coseno vectorizada (numpy). Resultado en orden cronológico.
        Llama a _backfill_embeddings() antes de buscar para cubrir el historico cargado de disco.
        """
        import numpy as np

        self._backfill_embeddings()

        # Solo tareas con embedding disponible
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
        # argpartition es O(n) vs O(n log n) de argsort — importa con 500+ tareas
        top_idx = np.argpartition(scores, -k)[-k:]
        selected_ids = {candidates[i]["id"] for i in top_idx}

        # Cronológico para que el LLM lea el contexto con orden temporal natural
        return [t for t in self._tasks if t["id"] in selected_ids]

    # ── Contexto para el LLM ──────────────────────────────────────────────────

    def get_context(self, query: str = None) -> Optional[str]:
        """
        Devuelve hechos + tareas relevantes como texto para el LLM.

        query — tarea actual (usada para búsqueda semántica).
          Si hay > semantic_threshold tareas y query no es None, y Ollama
          está disponible → búsqueda semántica con nomic-embed-text.
          En cualquier otro caso → últimas n_recent en orden cronológico.
        """
        parts: list[str] = []

        if self._facts:
            parts.append(
                "[Known facts about this user/system]\n"
                + "\n".join(f"• {f}" for f in self._facts)
            )

        if self._tasks:
            use_semantic = (
                query is not None
                and len(self._tasks) > self.semantic_threshold
            )
            header = "[Memory — past tasks]"

            if use_semantic:
                try:
                    recent = self._semantic_search(query, top_k=self.n_recent)
                    header = "[Relevant past tasks — semantic search]"
                except Exception:
                    recent = self._tasks[-self.n_recent :]
            else:
                recent = self._tasks[-self.n_recent :]

            lines = []
            for e in recent:
                ts = e["timestamp"][:16].replace("T", " ")
                agents = ", ".join(e["agents_used"]) if e["agents_used"] else "?"
                lines.append(
                    f"• [{ts}] ({agents})\n"
                    f"  Task: {e['task'][:150]}\n"
                    f"  Result: {e['result'][:300]}"
                )
            parts.append(header + "\n" + "\n".join(lines))

        if not parts:
            return None

        return "\n\n".join(parts)[: self.max_context_chars]

    def __len__(self) -> int:
        return len(self._tasks)

"""
Skill plugin loader — patrón de OpenClaw/Hermes.
Permite añadir herramientas nuevas sin modificar código existente.

Estructura:
  skills/
    mi_skill.py    ← define funciones @tool + SKILL_METADATA opcional
    otro_skill.py

SKILL_METADATA (opcional por archivo):
  SKILL_METADATA = {
      "agents": ["coder", "pc_controller"],  # omitir = todos los agentes
      "description": "Qué hace esta skill",
  }

Uso: colocar un .py con @tool en skills/ — se carga automáticamente.
Archivos que empiecen con _ son ignorados.
"""
import importlib.util
from pathlib import Path

from langchain_core.tools import BaseTool


_SKILLS_CACHE: dict[str, list[BaseTool]] | None = None


def load_skills(skills_dir: str | Path | None = None) -> dict[str, list[BaseTool]]:
    """
    Carga todas las funciones @tool de skills/*.py y las agrupa por agente.
    El resultado se cachea en memoria — el escaneo de disco ocurre una sola vez.

    Returns:
        {"*": [tools para todos], "coder": [tools solo para coder], ...}
    """
    global _SKILLS_CACHE
    if _SKILLS_CACHE is not None:
        return _SKILLS_CACHE

    if skills_dir is None:
        # Ruta absoluta relativa a este archivo — funciona sea cual sea el CWD
        skills_dir = Path(__file__).parent.parent / "skills"

    path = Path(skills_dir)
    if not path.exists():
        _SKILLS_CACHE = {}
        return _SKILLS_CACHE

    result: dict[str, list[BaseTool]] = {}
    total = 0

    for skill_file in sorted(path.glob("*.py")):
        if skill_file.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"omniforge_skill_{skill_file.stem}", skill_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            tools = [
                obj
                for attr in dir(module)
                if not attr.startswith("_")
                for obj in [getattr(module, attr)]
                if isinstance(obj, BaseTool)
            ]
            if not tools:
                continue

            metadata = getattr(module, "SKILL_METADATA", {})
            target_agents: list[str] = metadata.get("agents") or ["*"]

            for agent in target_agents:
                bucket = result.setdefault(agent, [])
                existing = {t.name for t in bucket}
                for t in tools:
                    if t.name not in existing:
                        bucket.append(t)
                        existing.add(t.name)

            total += len(tools)
        except Exception as e:
            print(f"[Skills] Error cargando {skill_file.name}: {e}")

    if total:
        agents_summary = ", ".join(k for k in result if k != "*")
        print(f"[Skills] {total} skill(s) cargado(s) "
              f"({'todos los agentes' if '*' in result else agents_summary})")

    _SKILLS_CACHE = result
    return _SKILLS_CACHE


def merge_skills(base_tools: list[BaseTool],
                 skill_map: dict[str, list[BaseTool]],
                 agent_name: str) -> list[BaseTool]:
    """
    Combina las tools base de un agente con las skills cargadas.
    Las skills para '*' se añaden a todos los agentes.
    Evita duplicados por nombre.
    """
    existing = {t.name for t in base_tools}
    extra: list[BaseTool] = []

    for bucket_key in ("*", agent_name):
        for t in skill_map.get(bucket_key, []):
            if t.name not in existing:
                extra.append(t)
                existing.add(t.name)

    return base_tools + extra
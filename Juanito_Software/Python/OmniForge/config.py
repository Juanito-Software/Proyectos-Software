"""
OmniForge — configuración central.
Cambiar modelo, timeouts o rutas aquí sin tocar lógica del agente.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()   # carga .env si existe — las vars de entorno tienen prioridad


@dataclass
class LLMConfig:
    provider: str = "ollama"          # ollama | anthropic | openai | google
    model: str = "qwen3:8b"
    base_url: Optional[str] = "http://localhost:11434"
    temperature: float = 0.0
    max_tokens: int = 4096
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
                                                          or os.getenv("OPENAI_API_KEY")
                                                          or os.getenv("GOOGLE_API_KEY"))


@dataclass
class ToolConfig:
    terminal_timeout: int = 60        # segundos máx por comando
    browser_headless: bool = True
    filesystem_root: Optional[str] = None   # None = sin restricción


@dataclass
class ScreenConfig:
    screenshot_dir: str = "screenshots"     # carpeta donde se guardan capturas
    failsafe: bool = True                   # mover ratón a esquina top-left = parada de emergencia
    action_pause: float = 0.1              # pausa entre acciones de pyautogui (segundos)
    max_screenshots: int = 50              # rotar capturas antiguas al superar este límite (0 = sin límite)


@dataclass
class AgentConfig:
    max_iterations: int = 20
    max_retries: int = 3
    verbose: bool = True


@dataclass
class VisionConfig:
    engine: str = "ocr"                      # ocr | ollama | anthropic | openai
    model: str = "llava:latest"              # modelo de visión (ollama) o claude-opus-4-5 / gpt-4o
    base_url: str = "http://localhost:11434" # base_url para ollama
    api_key: Optional[str] = None           # None → hereda la clave de LLMConfig
    # Ruta al ejecutable de Tesseract. None = detección automática.
    # Windows: suele ser r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    tesseract_cmd: Optional[str] = field(default_factory=lambda: os.getenv("TESSERACT_CMD"))


@dataclass
class EvaluatorConfig:
    enabled: bool = True
    eval_dir: str = field(default_factory=lambda: str(Path.home() / ".omniforge"))
    analyze_every: int = 10    # analizar patrones cada N tareas completadas


@dataclass
class LoggingConfig:
    enabled: bool = True
    log_dir: str = field(default_factory=lambda: str(Path(__file__).parent / "logs"))
    # LangSmith: pon LANGCHAIN_API_KEY en .env y langsmith_project aquí para activarlo.
    # LANGCHAIN_TRACING_V2=true se activa automáticamente si hay clave + proyecto.
    langsmith_project: Optional[str] = None


@dataclass
class MemoryConfig:
    enabled: bool = True
    path: str = field(default_factory=lambda: str(Path.home() / ".omniforge" / "memory.json"))
    max_entries: int = 1000
    max_context_chars: int = 2000
    n_recent: int = 8                  # cuántas memorias recientes inyectar al LLM
    max_facts: int = 50                # límite de hechos estructurados acumulados
    extract_facts: bool = True         # extrae hechos durables con LLM al final de cada tarea
    semantic_threshold: int = 500      # activar búsqueda semántica a partir de este nº de tareas
    # Modelo de embeddings vía Ollama. Requiere: ollama pull nomic-embed-text
    embedding_model: str = "nomic-embed-text"
    embedding_base_url: str = "http://localhost:11434"


@dataclass
class OmniForgeConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    tools: ToolConfig = field(default_factory=ToolConfig)
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    evaluator: EvaluatorConfig = field(default_factory=EvaluatorConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)


# Instancia global — importar desde aquí
CONFIG = OmniForgeConfig()

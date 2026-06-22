"""
OmniForge — configuración central.
Cambiar modelo, timeouts o rutas aquí sin tocar lógica del agente.
"""
from dataclasses import dataclass, field
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


@dataclass
class OmniForgeConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    tools: ToolConfig = field(default_factory=ToolConfig)
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)


# Instancia global — importar desde aquí
CONFIG = OmniForgeConfig()

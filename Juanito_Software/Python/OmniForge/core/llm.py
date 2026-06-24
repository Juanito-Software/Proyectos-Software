"""
Abstracción LLM — el agente nunca importa un provider directamente.
Cambiar provider = cambiar CONFIG.llm, nada más.

Providers instalados por defecto: ollama
Providers opcionales (ver requirements.txt):
  pip install langchain-anthropic    → provider="anthropic"
  pip install langchain-openai       → provider="openai"
  pip install langchain-google-genai → provider="google"
"""
from langchain_core.language_models.chat_models import BaseChatModel
from config import OmniForgeConfig


def build_llm_list(config: OmniForgeConfig) -> list[BaseChatModel]:
    """
    Devuelve el LLM primario + la cadena de fallbacks configurados.
    Hermes pattern: si el primario falla, se intenta el siguiente en orden.
    La lista siempre tiene al menos un elemento (el primario).
    """
    primary = build_llm(config)
    if not config.llm.fallback_providers:
        return [primary]

    fallbacks = [primary]
    for fb in config.llm.fallback_providers:
        try:
            from dataclasses import replace as dc_replace
            fb_llm = dc_replace(
                config.llm,
                provider=fb.get("provider", config.llm.provider),
                model=fb.get("model", config.llm.model),
                base_url=fb.get("base_url", config.llm.base_url),
                api_key=fb.get("api_key") or config.llm.api_key,
                fallback_providers=[],  # no encadenar recursivamente
            )
            fb_config = dc_replace(config, llm=fb_llm)
            fallbacks.append(build_llm(fb_config))
        except Exception as e:
            print(f"[LLM] Fallback no configurado: {e}")
    return fallbacks


def build_llm(config: OmniForgeConfig) -> BaseChatModel:
    """
    Construye y devuelve el LLM configurado.
    El agente recibe un BaseChatModel sin saber el proveedor.
    """
    provider = config.llm.provider.lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=config.llm.model,
            base_url=config.llm.base_url,
            temperature=config.llm.temperature,
            num_predict=config.llm.max_tokens,
            think=False,  # desactiva thinking en qwen3 → misma velocidad que 7b, mejor instrucción
        )

    if provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic  # type: ignore[import]
        except ImportError:
            raise ImportError(
                "langchain-anthropic no está instalado.\n"
                "Ejecuta: pip install langchain-anthropic\n"
                "O descomenta la línea en requirements.txt."
            )
        return ChatAnthropic(
            model=config.llm.model,
            api_key=config.llm.api_key,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )

    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI  # type: ignore[import]
        except ImportError:
            raise ImportError(
                "langchain-openai no está instalado.\n"
                "Ejecuta: pip install langchain-openai\n"
                "O descomenta la línea en requirements.txt."
            )
        return ChatOpenAI(
            model=config.llm.model,
            api_key=config.llm.api_key,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )

    if provider == "google":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import]
        except ImportError:
            raise ImportError(
                "langchain-google-genai no está instalado.\n"
                "Ejecuta: pip install langchain-google-genai\n"
                "O descomenta la línea en requirements.txt."
            )
        return ChatGoogleGenerativeAI(
            model=config.llm.model,
            google_api_key=config.llm.api_key,
            temperature=config.llm.temperature,
            max_output_tokens=config.llm.max_tokens,
        )

    raise ValueError(
        f"Provider '{provider}' no soportado. Opciones: ollama, anthropic, openai, google"
    )

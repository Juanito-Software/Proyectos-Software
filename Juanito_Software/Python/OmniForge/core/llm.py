"""
Abstracción LLM — el agente nunca importa un provider directamente.
Cambiar provider = cambiar CONFIG.llm, nada más.
"""
from langchain_core.language_models.chat_models import BaseChatModel
from config import OmniForgeConfig


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
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=config.llm.model,
            api_key=config.llm.api_key,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.llm.model,
            api_key=config.llm.api_key,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=config.llm.model,
            google_api_key=config.llm.api_key,
            temperature=config.llm.temperature,
            max_output_tokens=config.llm.max_tokens,
        )

    raise ValueError(f"Provider '{provider}' no soportado. Opciones: ollama, anthropic, openai, google")

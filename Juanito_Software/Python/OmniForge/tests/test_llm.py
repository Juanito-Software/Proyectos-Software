"""Tests de la fábrica de LLM — sin conexión a red (solo construcción)."""
import pytest

from config import OmniForgeConfig
from core.llm import build_llm, build_llm_list


class TestBuildLlm:
    def test_provider_ollama_devuelve_chat_ollama(self):
        config = OmniForgeConfig()
        llm = build_llm(config)
        assert llm.__class__.__name__ == "ChatOllama"

    def test_provider_no_soportado_lanza_valueerror(self):
        config = OmniForgeConfig()
        config.llm.provider = "telepata"
        with pytest.raises(ValueError):
            build_llm(config)

    def test_build_llm_list_siempre_devuelve_al_menos_el_primario(self):
        config = OmniForgeConfig()
        config.llm.fallback_providers = []
        lista = build_llm_list(config)
        assert len(lista) == 1
        assert lista[0].__class__.__name__ == "ChatOllama"

    def test_build_llm_list_con_fallbacks(self):
        config = OmniForgeConfig()
        config.llm.fallback_providers = [
            {"provider": "ollama", "model": "qwen2.5:7b"},
        ]
        lista = build_llm_list(config)
        assert len(lista) == 2
        assert [l.__class__.__name__ for l in lista] == ["ChatOllama", "ChatOllama"]
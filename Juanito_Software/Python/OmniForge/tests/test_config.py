"""Tests de la configuración central — valores por defecto y campos clave."""
from config import (
    OmniForgeConfig,
    LLMConfig,
    ToolConfig,
    ScreenConfig,
    AgentConfig,
    VisionConfig,
    EvaluatorConfig,
    LoggingConfig,
    MemoryConfig,
)


def test_config_por_defecto_crea_todas_las_secciones():
    config = OmniForgeConfig()
    assert isinstance(config.llm, LLMConfig)
    assert isinstance(config.tools, ToolConfig)
    assert isinstance(config.screen, ScreenConfig)
    assert isinstance(config.agent, AgentConfig)
    assert isinstance(config.vision, VisionConfig)
    assert isinstance(config.evaluator, EvaluatorConfig)
    assert isinstance(config.logging, LoggingConfig)
    assert isinstance(config.memory, MemoryConfig)


def test_llm_por_defecto_es_ollama():
    llm = LLMConfig()
    assert llm.provider == "ollama"
    assert llm.model == "qwen3:8b"
    assert llm.temperature == 0.0
    assert llm.max_tokens == 4096
    assert llm.fallback_providers == [{"provider": "ollama", "model": "qwen2.5:7b"}]


def test_agente_limita_iteraciones_y_reintentos():
    config = AgentConfig()
    assert config.max_iterations == 20
    assert config.max_retries == 3


def test_evaluador_y_logging_activados_por_defecto():
    assert EvaluatorConfig().enabled is True
    assert LoggingConfig().enabled is True


def test_memory_tiene_limites_sensatos():
    memoria = MemoryConfig()
    assert memoria.max_entries == 1000
    assert memoria.n_recent == 8
    assert memoria.max_facts == 50
    assert memoria.semantic_threshold == 500
    assert memoria.extract_facts is True


def test_vision_usa_ollama_por_defecto():
    vision = VisionConfig()
    assert vision.engine == "ollama"
    assert vision.model == "llava:7b"


def test_concentracion_de_license_config_operativo():
    # smoke-test: la config no rompe al importarla dos veces (global CONFIG)
    from config import CONFIG
    assert CONFIG.screen.failsafe is True
    assert CONFIG.tools.terminal_timeout == 60
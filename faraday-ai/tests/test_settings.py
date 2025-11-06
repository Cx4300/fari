"""
Test Settings Configuration
"""

import pytest
from config.settings import Settings, LLMConfig, RAGConfig


def test_settings_initialization():
    """Test settings initialization"""
    settings = Settings()

    assert settings.llm is not None
    assert settings.rag is not None
    assert settings.tts is not None
    assert settings.agent is not None
    assert settings.tools is not None


def test_llm_config():
    """Test LLM configuration"""
    config = LLMConfig()

    assert config.primary_provider in ["openai", "anthropic", "local"]
    assert isinstance(config.temperature, float)
    assert isinstance(config.max_tokens, int)
    assert config.max_tokens > 0


def test_rag_config():
    """Test RAG configuration"""
    config = RAGConfig()

    assert config.chunk_size > 0
    assert config.chunk_overlap >= 0
    assert config.top_k_results > 0
    assert len(config.supported_extensions) > 0


def test_settings_validation():
    """Test settings validation"""
    settings = Settings()
    validation = settings.validate()

    assert isinstance(validation, dict)
    assert "valid" in validation
    assert "issues" in validation
    assert "warnings" in validation


def test_get_enabled_tools():
    """Test getting enabled tools"""
    settings = Settings()
    tools = settings.get_enabled_tools()

    assert isinstance(tools, list)


def test_is_tool_enabled():
    """Test checking if tool is enabled"""
    settings = Settings()

    # Should have some default tools enabled
    # (actual result depends on .env configuration)
    result = settings.is_tool_enabled("calculator")
    assert isinstance(result, bool)

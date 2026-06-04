from app.core.config import Settings, get_settings
from app.llm.base import BaseLLMClient
from app.llm.mock_client import MockLLMClient


def get_llm_client(settings: Settings | None = None) -> BaseLLMClient:
    cfg = settings or get_settings()
    provider = cfg.llm_provider
    if provider == "mock":
        return MockLLMClient()
    if provider == "vertex":
        from app.llm.vertex_ai_client import VertexAIClient

        return VertexAIClient(cfg)
    if provider == "openai":
        from app.llm.openai_client import OpenAIClient

        return OpenAIClient(cfg)
    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}")

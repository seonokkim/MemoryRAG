import importlib
import sys

import pytest

from app.core.config import Settings
from app.llm.base import BaseLLMClient
from app.llm.factory import get_llm_client
from app.llm.mock_client import MockLLMClient


class TestLLMFactory:
    def test_mock_provider_returns_mock_client(self) -> None:
        client = get_llm_client(Settings(llm_provider="mock"))
        assert isinstance(client, MockLLMClient)
        assert isinstance(client, BaseLLMClient)

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown LLM_PROVIDER"):
            get_llm_client(Settings.model_construct(llm_provider="invalid"))

    def test_vertex_not_imported_when_mock_selected(self) -> None:
        for name in list(sys.modules):
            if name in ("app.llm.vertex_ai_client", "app.llm.openai_client"):
                del sys.modules[name]
        get_llm_client(Settings(llm_provider="mock"))
        assert "app.llm.vertex_ai_client" not in sys.modules
        assert "app.llm.openai_client" not in sys.modules

    def test_vertex_requires_project_id(self) -> None:
        for name in ("app.llm.vertex_ai_client", "app.llm"):
            sys.modules.pop(name, None)
        importlib.invalidate_caches()
        with pytest.raises(RuntimeError, match="VERTEX_PROJECT_ID"):
            get_llm_client(Settings(llm_provider="vertex", vertex_project_id=""))

    def test_vertex_lazy_import_when_selected(self) -> None:
        for name in ("app.llm.vertex_ai_client", "app.llm"):
            sys.modules.pop(name, None)
        importlib.invalidate_caches()
        from app.llm import get_llm_client as reload_get

        client = reload_get(
            Settings(llm_provider="vertex", vertex_project_id="demo-project")
        )
        assert client.__class__.__name__ == "VertexAIClient"

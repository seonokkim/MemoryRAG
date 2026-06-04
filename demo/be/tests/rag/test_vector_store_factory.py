import sys

import pytest

from app.core.config import Settings
from app.rag.vector_store.factory import get_vector_store
from app.rag.vector_store.sql_fallback import SqlFallbackVectorStore


class TestVectorStoreFactoryPolicy:
    def test_none_returns_sql_fallback(self) -> None:
        store = get_vector_store(Settings(vector_store_provider="none"))
        assert isinstance(store, SqlFallbackVectorStore)

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown VECTOR_STORE_PROVIDER"):
            get_vector_store(Settings.model_construct(vector_store_provider="invalid"))

    def test_default_mode_does_not_import_chroma_or_vertex_modules(self) -> None:
        for name in list(sys.modules):
            if name.startswith("app.rag.vector_store.chroma"):
                del sys.modules[name]
            if name.startswith("app.rag.vector_store.vertex"):
                del sys.modules[name]
        get_vector_store(Settings(vector_store_provider="none"))
        assert "app.rag.vector_store.chroma_store" not in sys.modules
        assert "app.rag.vector_store.vertex_vector_search" not in sys.modules

    def test_chroma_lazy_import_only_when_selected(self) -> None:
        sys.modules.pop("app.rag.vector_store.chroma_store", None)
        store = get_vector_store(Settings(vector_store_provider="chroma"))
        assert store.provider_name == "chroma"
        assert "app.rag.vector_store.chroma_store" in sys.modules

    def test_vertex_lazy_import_only_when_selected(self) -> None:
        sys.modules.pop("app.rag.vector_store.vertex_vector_search", None)
        store = get_vector_store(
            Settings(vector_store_provider="vertex", vertex_project_id="demo")
        )
        assert store.provider_name == "vertex_vector_search"
        assert "app.rag.vector_store.vertex_vector_search" in sys.modules

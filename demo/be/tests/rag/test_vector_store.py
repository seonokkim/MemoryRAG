from app.core.config import Settings
from app.rag.vector_store import describe_vector_backend, get_vector_store
from app.rag.vector_store.sql_fallback import SqlFallbackVectorStore


class TestVectorStoreFactory:
    def test_none_uses_sql_fallback(self) -> None:
        store = get_vector_store(Settings(vector_store_provider="none"))
        assert isinstance(store, SqlFallbackVectorStore)
        assert describe_vector_backend(Settings(vector_store_provider="none")) == "mysql+sql_fallback"

    def test_chroma_without_optional_deps_is_unavailable(self) -> None:
        settings = Settings(vector_store_provider="chroma")
        store = get_vector_store(settings)
        assert store.provider_name == "chroma"
        assert store.is_available() is False
        assert "unavailable" in describe_vector_backend(settings)

    def test_vertex_without_ids_is_unconfigured(self) -> None:
        from app.rag.vector_store.vertex_vector_search import VertexVectorSearchStore

        store = get_vector_store(
            Settings(vector_store_provider="vertex", vertex_project_id="demo-project")
        )
        assert isinstance(store, VertexVectorSearchStore)
        assert store.is_available() is False
        assert "unconfigured" in describe_vector_backend(
            Settings(vector_store_provider="vertex", vertex_project_id="demo-project")
        )

    def test_vertex_with_ids_is_configured(self) -> None:
        from app.rag.vector_store.vertex_vector_search import VertexVectorSearchStore

        settings = Settings(
            vector_store_provider="vertex",
            vertex_project_id="demo-project",
            vertex_vector_index_id="idx-1",
            vertex_vector_endpoint_id="ep-1",
            vertex_vector_deployed_index_id="deployed-1",
        )
        store = get_vector_store(settings)
        assert isinstance(store, VertexVectorSearchStore)
        assert store.is_available() is True
        assert describe_vector_backend(settings) == "vertex_ai_vector_search"

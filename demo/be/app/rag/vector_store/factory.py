from app.core.config import Settings, get_settings
from app.rag.vector_store.base import VectorStoreBackend
from app.rag.vector_store.sql_fallback import SqlFallbackVectorStore


def get_vector_store(settings: Settings | None = None) -> VectorStoreBackend:
    cfg = settings or get_settings()
    provider = cfg.vector_store_provider
    if provider == "none":
        return SqlFallbackVectorStore(cfg)
    if provider == "chroma":
        from app.rag.vector_store.chroma_store import ChromaVectorStore

        return ChromaVectorStore(cfg)
    if provider == "vertex":
        from app.rag.vector_store.vertex_vector_search import VertexVectorSearchStore

        return VertexVectorSearchStore(cfg)
    raise ValueError(f"Unknown VECTOR_STORE_PROVIDER: {provider!r}")


def describe_vector_backend(settings: Settings | None = None) -> str:
    store = get_vector_store(settings)
    if store.provider_name == "sql_fallback":
        return "mysql+sql_fallback"
    if store.provider_name == "vertex_vector_search":
        if store.is_available():
            return "vertex_ai_vector_search"
        return "vertex_ai_vector_search(unconfigured)"
    if store.provider_name == "chroma":
        if store.is_available():
            return "chroma+llamaindex"
        return "chroma(unavailable)+sql_fallback"
    return store.provider_name

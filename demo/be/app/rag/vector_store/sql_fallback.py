from app.core.config import Settings
from app.rag.vector_store.base import VectorRecord, VectorSearchHit, VectorStoreBackend


class SqlFallbackVectorStore(VectorStoreBackend):
    """No external vector index; retrieval uses MySQL keyword/SQL paths only."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings

    @property
    def provider_name(self) -> str:
        return "sql_fallback"

    def is_available(self) -> bool:
        return True

    def upsert(self, collection: str, records: list[VectorRecord]) -> list[str]:
        return [r.id for r in records]

    def search(
        self,
        collection: str,
        query: str,
        *,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[VectorSearchHit]:
        return []

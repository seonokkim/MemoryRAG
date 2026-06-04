from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class VectorRecord:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass
class VectorSearchHit:
    id: str
    text: str
    score: float
    metadata: dict = field(default_factory=dict)


class VectorStoreBackend(ABC):
    """Pluggable vector backend; MySQL remains source of truth for chunk text and metadata."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """True when configured and safe to attempt vector upsert/search."""
        ...

    @abstractmethod
    def upsert(self, collection: str, records: list[VectorRecord]) -> list[str]:
        """Upsert embeddings; returns vector ids aligned with records."""
        ...

    @abstractmethod
    def search(
        self,
        collection: str,
        query: str,
        *,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[VectorSearchHit]:
        ...

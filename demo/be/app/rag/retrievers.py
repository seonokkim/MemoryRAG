from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.rag.vector_store import VectorRecord, get_vector_store
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.user_repository import UserRepository

KNOWLEDGE_COLLECTION = "golf_knowledge"
MEMORY_COLLECTION = "user_memory"


@dataclass
class RetrievedChunk:
    content: str
    source: str
    score: float
    metadata: dict


class KnowledgeRetriever:
    def __init__(self, db: Session) -> None:
        self.repo = KnowledgeRepository(db)
        self.settings = get_settings()
        self.vector_store = get_vector_store(self.settings)

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        hits = self._retrieve_from_vector_store(query, top_k=top_k)
        if hits:
            return hits
        return self._retrieve_from_sql(query, top_k=top_k)

    def _retrieve_from_vector_store(self, query: str, top_k: int) -> list[RetrievedChunk]:
        if self.settings.vector_store_provider == "none":
            return []
        raw_hits = self.vector_store.search(
            KNOWLEDGE_COLLECTION,
            query,
            top_k=top_k,
        )
        if not raw_hits:
            return []
        chunks = []
        for hit in raw_hits:
            content = hit.text
            if not content and hit.id:
                row = self.repo.get_chunk_by_vector_id(hit.id)
                if row:
                    content = row.content
            if content:
                chunks.append(
                    RetrievedChunk(
                        content=content,
                        source="golf_knowledge",
                        score=hit.score,
                        metadata=hit.metadata,
                    )
                )
        return chunks

    def _retrieve_from_sql(self, query: str, top_k: int) -> list[RetrievedChunk]:
        chunks = self.repo.search_chunks_sql(query, limit=top_k)
        if not chunks:
            chunks = self.repo.all_chunks(limit=top_k)
        return [
            RetrievedChunk(
                content=c.content,
                source="golf_knowledge",
                score=0.75,
                metadata=c.metadata_json or {},
            )
            for c in chunks
        ]


class MemoryRetriever:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)
        self.settings = get_settings()
        self.vector_store = get_vector_store(self.settings)

    def retrieve(self, user_id: int, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        hits = self._retrieve_from_vector_store(user_id, query, top_k=top_k)
        if hits:
            return hits
        return self._retrieve_from_sql(user_id, query, top_k=top_k)

    def _retrieve_from_vector_store(
        self, user_id: int, query: str, top_k: int
    ) -> list[RetrievedChunk]:
        if self.settings.vector_store_provider == "none":
            return []
        raw_hits = self.vector_store.search(
            MEMORY_COLLECTION,
            query,
            top_k=top_k,
            filters={"user_id": user_id},
        )
        return [
            RetrievedChunk(
                content=hit.text or "",
                source="long_term_memory",
                score=hit.score,
                metadata={**hit.metadata, "user_id": user_id},
            )
            for hit in raw_hits
            if hit.text
        ]

    def _retrieve_from_sql(self, user_id: int, query: str, top_k: int) -> list[RetrievedChunk]:
        memories = self.repo.list_active_memories(user_id, limit=top_k)
        query_l = query.lower()
        ranked = sorted(
            memories,
            key=lambda m: int(any(w in m.content.lower() for w in query_l.split()[:5])),
            reverse=True,
        )
        return [
            RetrievedChunk(
                content=m.content,
                source="long_term_memory",
                score=float(m.confidence or 0.7),
                metadata={"memory_type": m.memory_type},
            )
            for m in ranked[:top_k]
        ]

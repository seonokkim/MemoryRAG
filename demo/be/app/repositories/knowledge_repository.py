from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KnowledgeChunk, KnowledgeDocument


class KnowledgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_documents(self) -> list[KnowledgeDocument]:
        return list(self.db.scalars(select(KnowledgeDocument)).all())

    def add_document(self, doc: KnowledgeDocument) -> KnowledgeDocument:
        self.db.add(doc)
        self.db.flush()
        return doc

    def add_chunk(self, chunk: KnowledgeChunk) -> KnowledgeChunk:
        self.db.add(chunk)
        self.db.flush()
        return chunk

    def search_chunks_sql(self, query: str, limit: int = 5) -> list[KnowledgeChunk]:
        pattern = f"%{query[:80]}%"
        stmt = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.content.ilike(pattern))
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def all_chunks(self, limit: int = 100) -> list[KnowledgeChunk]:
        stmt = select(KnowledgeChunk).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_chunk_by_vector_id(self, vector_id: str) -> KnowledgeChunk | None:
        stmt = select(KnowledgeChunk).where(KnowledgeChunk.vector_id == vector_id).limit(1)
        return self.db.scalars(stmt).first()

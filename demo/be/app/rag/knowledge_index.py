from sqlalchemy.orm import Session

from app.rag.ingestion import chunk_text
from app.rag.retrievers import KNOWLEDGE_COLLECTION, KnowledgeRetriever
from app.rag.vector_store import VectorRecord, get_vector_store
from app.repositories.knowledge_repository import KnowledgeRepository
from app.models import KnowledgeChunk, KnowledgeDocument


class KnowledgeIndexService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.retriever = KnowledgeRetriever(db)
        self.vector_store = get_vector_store()

    def ingest_document(
        self, title: str, content: str, category: str, source: str = "seed"
    ) -> tuple[KnowledgeDocument, list[KnowledgeChunk]]:
        doc = KnowledgeDocument(
            title=title,
            content=content,
            category=category,
            source=source,
        )
        self.repo.add_document(doc)
        chunks: list[KnowledgeChunk] = []
        vector_records: list[VectorRecord] = []
        for idx, piece in enumerate(chunk_text(content)):
            vector_id = f"doc-{doc.id}-chunk-{idx}"
            chunk = KnowledgeChunk(
                document_id=doc.id,
                chunk_index=idx,
                content=piece,
                metadata_json={"category": category, "title": title, "collection": KNOWLEDGE_COLLECTION},
                vector_id=vector_id,
            )
            self.repo.add_chunk(chunk)
            chunks.append(chunk)
            vector_records.append(
                VectorRecord(
                    id=vector_id,
                    text=piece,
                    metadata={
                        "category": category,
                        "title": title,
                        "document_id": doc.id,
                        "collection": KNOWLEDGE_COLLECTION,
                    },
                )
            )
        if vector_records:
            ids = self.vector_store.upsert(KNOWLEDGE_COLLECTION, vector_records)
            for chunk, vid in zip(chunks, ids, strict=True):
                chunk.vector_id = vid
        return doc, chunks

    def query(self, text: str, top_k: int = 5):
        return self.retriever.retrieve(text, top_k=top_k)

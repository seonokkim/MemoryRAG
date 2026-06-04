from app.core.config import Settings
from app.rag.llama_index_setup import get_chroma_persist_dir, is_llama_index_available
from app.rag.vector_store.base import VectorRecord, VectorSearchHit, VectorStoreBackend


class ChromaVectorStore(VectorStoreBackend):
    """Local MVP vector store via LlamaIndex + Chroma persistence."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._persist_dir = get_chroma_persist_dir()

    @property
    def provider_name(self) -> str:
        return "chroma"

    def is_available(self) -> bool:
        return is_llama_index_available()

    def upsert(self, collection: str, records: list[VectorRecord]) -> list[str]:
        if not self.is_available() or not records:
            return [r.id for r in records]
        try:
            self._upsert_via_llama_index(collection, records)
        except Exception:
            pass
        return [r.id for r in records]

    def search(
        self,
        collection: str,
        query: str,
        *,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[VectorSearchHit]:
        if not self.is_available():
            return []
        try:
            return self._search_via_llama_index(collection, query, top_k=top_k, filters=filters)
        except Exception:
            return []

    def _upsert_via_llama_index(self, collection: str, records: list[VectorRecord]) -> None:
        from llama_index.core import Document, VectorStoreIndex
        from llama_index.core.storage.storage_context import StorageContext
        from llama_index.vector_stores.chroma import ChromaVectorStore as LIChromaVectorStore

        import chromadb

        client = chromadb.PersistentClient(path=str(self._persist_dir))
        chroma_collection = client.get_or_create_collection(collection)
        vector_store = LIChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        docs = [
            Document(text=r.text, metadata=r.metadata, id_=r.id)
            for r in records
        ]
        VectorStoreIndex.from_documents(docs, storage_context=storage_context)

    def _search_via_llama_index(
        self,
        collection: str,
        query: str,
        *,
        top_k: int,
        filters: dict | None,
    ) -> list[VectorSearchHit]:
        from llama_index.core import VectorStoreIndex
        from llama_index.core.storage.storage_context import StorageContext
        from llama_index.vector_stores.chroma import ChromaVectorStore as LIChromaVectorStore

        import chromadb

        client = chromadb.PersistentClient(path=str(self._persist_dir))
        chroma_collection = client.get_or_create_collection(collection)
        vector_store = LIChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        retriever = index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)
        hits: list[VectorSearchHit] = []
        for node in nodes:
            meta = dict(node.metadata or {})
            if filters and not _metadata_matches(meta, filters):
                continue
            hits.append(
                VectorSearchHit(
                    id=node.node_id,
                    text=node.get_content(),
                    score=float(node.score or 0.0),
                    metadata=meta,
                )
            )
        return hits[:top_k]


def _metadata_matches(metadata: dict, filters: dict) -> bool:
    return all(metadata.get(k) == v for k, v in filters.items())

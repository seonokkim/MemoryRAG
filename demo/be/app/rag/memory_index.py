from sqlalchemy.orm import Session

from app.rag.retrievers import MemoryRetriever


class MemoryIndexService:
    def __init__(self, db: Session) -> None:
        self.retriever = MemoryRetriever(db)

    def query(self, user_id: int, text: str, top_k: int = 5):
        return self.retriever.retrieve(user_id, text, top_k=top_k)

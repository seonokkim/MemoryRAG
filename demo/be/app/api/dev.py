from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.rag.knowledge_index import KnowledgeIndexService
from app.rag.vector_store import describe_vector_backend
from app.schemas.dev import ConversationTraceResponse, IngestKnowledgeResponse, PromptVersionItem
from app.services.eval_service import EvalService

router = APIRouter(prefix="/dev", tags=["dev"])


@router.get("/conversations/{conversation_id}/trace", response_model=ConversationTraceResponse)
def get_trace(
    conversation_id: int, db: Session = Depends(get_db)
) -> ConversationTraceResponse:
    return EvalService(db).get_conversation_trace(conversation_id)


@router.get("/prompt-versions", response_model=list[PromptVersionItem])
def list_prompt_versions(db: Session = Depends(get_db)) -> list[PromptVersionItem]:
    return EvalService(db).list_prompt_versions()


@router.post("/ingest-knowledge", response_model=IngestKnowledgeResponse)
def ingest_knowledge(db: Session = Depends(get_db)) -> IngestKnowledgeResponse:
    from app.data.knowledge_seed import KNOWLEDGE_DOCS

    service = KnowledgeIndexService(db)
    doc_count = 0
    chunk_count = 0
    for item in KNOWLEDGE_DOCS:
        doc, chunks = service.ingest_document(
            title=item["title"],
            content=item["content"],
            category=item["category"],
        )
        doc_count += 1
        chunk_count += len(chunks)
    db.commit()
    return IngestKnowledgeResponse(
        documents_ingested=doc_count,
        chunks_ingested=chunk_count,
        vector_store=describe_vector_backend(),
    )

from pydantic import BaseModel


class PromptVersionItem(BaseModel):
    name: str
    version: str
    is_active: bool
    created_at: str


class ConversationTraceResponse(BaseModel):
    conversation_id: int
    workflow: str
    prompt_version: str
    latency_ms: int | None
    retrieved_chunk_count: int
    guardrail_status: str | None
    failure_type: str | None
    retrieved_sources: list[str]
    question_type: str | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    quality_status: str | None = None
    retry_count: int | None = None
    trace: dict


class IngestKnowledgeResponse(BaseModel):
    documents_ingested: int
    chunks_ingested: int
    vector_store: str

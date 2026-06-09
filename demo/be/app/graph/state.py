from typing import Any, TypedDict

from app.schemas.coach import StructuredCoachingOutput


class CoachState(TypedDict, total=False):
    user_id: int
    conversation_id: int
    user_message: str
    messages: list[dict[str, str]]
    question_type: str
    user_profile: dict[str, Any]
    recent_swing_sessions: list[dict[str, Any]]
    long_term_memories: list[dict[str, Any]]
    golf_knowledge_chunks: list[dict[str, Any]]
    structured_output: StructuredCoachingOutput | dict[str, Any]
    final_answer: str
    guardrail_status: str
    failure_type: str | None
    latency_ms: int
    trace: dict[str, Any]
    trace_id: str
    assistant_message_id: int
    retrieved_sources: list[str]
    prompt_version: str
    llm_provider: str
    llm_model: str
    retry_count: int
    quality_status: str
    quality_reasons: list[str]
    rewritten_query: str
    tool_results: dict[str, Any]

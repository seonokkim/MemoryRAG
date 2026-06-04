from pydantic import BaseModel, Field


class StructuredCoachingOutput(BaseModel):
    summary: str = ""
    cause: str = ""
    fix: str = ""
    recommended_drill: str = ""
    expected_effect: str = ""
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class CoachChatRequest(BaseModel):
    user_id: int
    message: str
    conversation_id: int | None = None


class CoachChatResponse(BaseModel):
    message_id: int
    conversation_id: int
    answer: str
    structured_output: StructuredCoachingOutput | None = None
    sources: list[str] = Field(default_factory=list)
    latency_ms: int
    trace_id: str
    guardrail_status: str = "passed"
    failure_type: str | None = None

from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    user_id: int
    message_id: int
    feedback_type: str
    reason: str | None = None


class FeedbackResponse(BaseModel):
    id: int
    status: str = "saved"

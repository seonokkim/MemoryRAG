from datetime import datetime

from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    user_id: int
    name: str
    email: str | None = None
    level: str | None = None
    dominant_hand: str | None = None
    goal: str | None = None
    golfer_type: str | None = None
    current_main_issue: str | None = None
    preferred_feedback_style: str | None = None
    profile_summary: str | None = None
    memory_summary: list[str] = []

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str

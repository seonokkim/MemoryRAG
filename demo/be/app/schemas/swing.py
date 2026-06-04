from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SwingSessionCreate(BaseModel):
    club_type: str = "Driver"
    view_type: str = "Front"
    concern: str | None = "Slice"
    video_url: str | None = None


class SwingSessionItem(BaseModel):
    id: int
    user_id: int
    club_type: str | None
    view_type: str | None
    concern: str | None
    video_url: str | None
    score: int | None
    main_issue: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SwingAnalysisResponse(BaseModel):
    session_id: int
    score: int | None
    main_issue: str | None
    phase_summary: dict[str, Any] = Field(default_factory=dict)
    pose_metrics: dict[str, Any] = Field(default_factory=dict)
    diagnosis_text: str | None = None
    evidence_text: str | None = None
    priority_issue: str | None = None
    recommended_action: str | None = None

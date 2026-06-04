from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SwingSession(Base):
    __tablename__ = "swing_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    club_type: Mapped[str | None] = mapped_column(String(50))
    view_type: Mapped[str | None] = mapped_column(String(50))
    concern: Mapped[str | None] = mapped_column(String(255))
    video_url: Mapped[str | None] = mapped_column(String(500))
    score: Mapped[int | None] = mapped_column(Integer)
    main_issue: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="swing_sessions")
    analysis: Mapped["SwingAnalysisResult | None"] = relationship(
        back_populates="session", uselist=False
    )


class SwingAnalysisResult(Base):
    __tablename__ = "swing_analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    swing_session_id: Mapped[int] = mapped_column(
        ForeignKey("swing_sessions.id"), nullable=False, unique=True, index=True
    )
    phase_summary_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    pose_metrics_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    diagnosis_text: Mapped[str | None] = mapped_column(Text)
    evidence_text: Mapped[str | None] = mapped_column(Text)
    priority_issue: Mapped[str | None] = mapped_column(String(255))
    recommended_action: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    session: Mapped["SwingSession"] = relationship(back_populates="analysis")

from app.core.errors import NotFoundError, not_found
from app.models import SwingAnalysisResult, SwingSession
from app.repositories.swing_repository import SwingRepository
from app.schemas.swing import SwingAnalysisResponse, SwingSessionCreate, SwingSessionItem
from app.storage import get_storage_service
from sqlalchemy.orm import Session

MOCK_PHASES = {
    "phases": [
        {"name": "Address", "status": "stable"},
        {"name": "Backswing", "status": "stable"},
        {"name": "Top", "status": "caution"},
        {"name": "Downswing", "status": "needs_work"},
        {"name": "Impact", "status": "needs_work"},
        {"name": "Follow", "status": "caution"},
    ]
}

MOCK_POSE = {
    "shoulder_rotation_speed": 68,
    "hip_rotation_timing": 72,
    "knee_stability": 85,
    "swing_tempo": 88,
    "wrist_angle_at_impact": 61,
}


class SwingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SwingRepository(db)
        self.storage = get_storage_service()

    def list_sessions(self, user_id: int, limit: int = 10) -> list[SwingSessionItem]:
        sessions = self.repo.list_recent(user_id, limit=limit)
        return [SwingSessionItem.model_validate(s) for s in sessions]

    def get_analysis(self, session_id: int) -> SwingAnalysisResponse:
        session = self.repo.get_session_with_analysis(session_id)
        if not session:
            raise not_found("SwingSession", session_id)
        analysis = session.analysis
        if not analysis:
            raise not_found("SwingAnalysisResult", session_id)
        return SwingAnalysisResponse(
            session_id=session.id,
            score=session.score,
            main_issue=session.main_issue,
            phase_summary=analysis.phase_summary_json or {},
            pose_metrics=analysis.pose_metrics_json or {},
            diagnosis_text=analysis.diagnosis_text,
            evidence_text=analysis.evidence_text,
            priority_issue=analysis.priority_issue,
            recommended_action=analysis.recommended_action,
        )

    def create_mock_session(
        self, user_id: int, payload: SwingSessionCreate
    ) -> tuple[SwingSessionItem, SwingAnalysisResponse]:
        video_url = payload.video_url or self.storage.resolve_video_url("sample_swing.mp4")
        session = SwingSession(
            user_id=user_id,
            club_type=payload.club_type,
            view_type=payload.view_type,
            concern=payload.concern,
            video_url=video_url,
            score=82,
            main_issue="Early upper-body opening before impact",
        )
        self.repo.create_session(session)
        analysis = SwingAnalysisResult(
            swing_session_id=session.id,
            phase_summary_json=MOCK_PHASES,
            pose_metrics_json=MOCK_POSE,
            diagnosis_text="Upper body opens quickly early in the downswing.",
            evidence_text="Recent sessions show faster-than-average shoulder rotation in early downswing.",
            priority_issue="Early upper-body opening before impact",
            recommended_action="Lower-body lead drill · 10 minutes",
        )
        self.repo.create_analysis(analysis)
        self.db.commit()
        self.db.refresh(session)
        return (
            SwingSessionItem.model_validate(session),
            self.get_analysis(session.id),
        )

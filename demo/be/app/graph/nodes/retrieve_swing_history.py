from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.graph.state import CoachState
from app.repositories.swing_repository import SwingRepository


def retrieve_swing_history(state: CoachState, db: Session) -> dict:
    settings = get_settings()
    repo = SwingRepository(db)
    sessions = repo.list_recent(state["user_id"], limit=settings.recent_swing_limit)
    payload = []
    for s in sessions:
        item = {
            "id": s.id,
            "score": s.score,
            "main_issue": s.main_issue,
            "club_type": s.club_type,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        full = repo.get_session_with_analysis(s.id)
        if full and full.analysis:
            item["pose_metrics"] = full.analysis.pose_metrics_json
        payload.append(item)
    trace = dict(state.get("trace") or {})
    trace["retrieve_swing_history"] = {"count": len(payload)}
    failure = state.get("failure_type")
    if not payload and state.get("question_type") in ("swing_diagnosis", "progress_check"):
        failure = failure or "missing_swing_data"
    return {
        "recent_swing_sessions": payload,
        "trace": trace,
        "failure_type": failure,
    }

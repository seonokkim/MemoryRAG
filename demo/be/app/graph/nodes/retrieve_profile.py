from sqlalchemy.orm import Session

from app.graph.state import CoachState
from app.repositories.user_repository import UserRepository


def retrieve_profile(state: CoachState, db: Session) -> dict:
    repo = UserRepository(db)
    profile = repo.get_profile(state["user_id"])
    data = {}
    if profile:
        data = {
            "goal": profile.goal,
            "golfer_type": profile.golfer_type,
            "current_main_issue": profile.current_main_issue,
            "preferred_feedback_style": profile.preferred_feedback_style,
            "profile_summary": profile.profile_summary,
        }
    trace = dict(state.get("trace") or {})
    trace["retrieve_profile"] = {"found": bool(profile)}
    return {"user_profile": data, "trace": trace}

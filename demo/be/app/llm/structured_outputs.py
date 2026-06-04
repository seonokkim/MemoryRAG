from app.schemas.coach import StructuredCoachingOutput

QUESTION_TYPES = [
    "swing_diagnosis",
    "progress_check",
    "practice_recommendation",
    "golfer_profile",
    "general_golf_knowledge",
    "unclear",
]


def classify_by_keywords(message: str) -> str:
    text = message.lower()
    if any(w in text for w in ("slice", "slicing", "hook", "fade", "why do i", "diagnosis", "keep slicing")):
        return "swing_diagnosis"
    if any(w in text for w in ("improv", "better", "progress", "last time")):
        return "progress_check"
    if any(w in text for w in ("practice", "drill", "routine", "today")):
        return "practice_recommendation"
    if any(w in text for w in ("type", "profile", "kind of golfer", "who am i")):
        return "golfer_profile"
    if any(w in text for w in ("golf", "club", "tempo", "swing")):
        return "general_golf_knowledge"
    return "unclear"

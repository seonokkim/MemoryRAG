from typing import Any

from app.llm.base import BaseLLMClient
from app.llm.structured_outputs import classify_by_keywords
from app.schemas.coach import StructuredCoachingOutput


class MockLLMClient(BaseLLMClient):
    """Deterministic local LLM; no API keys required."""

    def classify_question_sync(self, message: str, context: dict[str, Any]) -> str:
        return classify_by_keywords(message)

    def generate_structured_answer_sync(
        self,
        message: str,
        question_type: str,
        context: dict[str, Any],
    ) -> StructuredCoachingOutput:
        profile = context.get("user_profile") or {}
        issue = profile.get("current_main_issue") or "early upper-body opening before impact"
        golfer_type = profile.get("golfer_type") or "fast upper-body rotation golfer"

        if question_type == "swing_diagnosis":
            return StructuredCoachingOutput(
                summary=(
                    "Recent swings show the upper body opening before the lower body "
                    "in the downswing, which can leave the clubface open at impact."
                ),
                cause="Upper body rotation starts before lower-body lead in the downswing",
                fix="Train lower-body lead and maintain shoulder closure longer",
                recommended_drill="Lower-body lead drill · 10 min · beginner",
                expected_effect="Reduced slice risk and improved direction control",
                sources=["swing_history", "golf_knowledge", "user_profile"],
                confidence=0.86,
            )
        if question_type == "progress_check":
            sessions = context.get("recent_swing_sessions") or []
            return StructuredCoachingOutput(
                summary=(
                    f"You have {len(sessions)} recent recorded swings. "
                    "Tempo and backswing path look more stable, but early upper-body "
                    "opening still appears before impact."
                ),
                cause=issue,
                fix="Keep tempo work and add lower-body lead focus",
                recommended_drill="Tempo consistency drill · 7 min",
                expected_effect="Steady score trend with better impact stability",
                sources=["swing_history", "user_profile"],
                confidence=0.82,
            )
        if question_type == "practice_recommendation":
            return StructuredCoachingOutput(
                summary="Today's plan: lower-body lead, shoulder closure, and tempo drills (25 min total).",
                cause=issue,
                fix="Sequential lower-body lead + shoulder closure training",
                recommended_drill="3-drill routine · 25 min total",
                expected_effect="Better impact stability and slice reduction",
                sources=["swing_history", "golf_knowledge", "user_profile"],
                confidence=0.84,
            )
        if question_type == "golfer_profile":
            return StructuredCoachingOutput(
                summary=f"You align with a '{golfer_type}' pattern with stable tempo but early upper-body opening.",
                cause=issue,
                fix="Prioritize lower-body lead in practice blocks",
                recommended_drill="Lower-body lead drill",
                expected_effect="Faster improvement on direction and impact",
                sources=["user_profile", "swing_history"],
                confidence=0.88,
            )
        return StructuredCoachingOutput(
            summary="I can help with swing diagnosis, progress checks, practice plans, and profile insights.",
            cause="",
            fix="Ask a more specific swing question or upload a new session",
            recommended_drill="",
            expected_effect="",
            sources=["golf_knowledge"],
            confidence=0.5,
        )

    def extract_memory_sync(
        self, message: str, answer: str, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        if self._slice_related(message):
            return [
                {
                    "memory_type": "user_goal",
                    "content": "User wants to reduce slice.",
                    "confidence": 0.85,
                }
            ]
        return []

    def _slice_related(self, message: str) -> bool:
        lower = message.lower()
        return any(term in lower for term in ("slice", "slicing", "hook"))

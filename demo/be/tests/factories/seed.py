from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import (
    Conversation,
    LongTermMemory,
    PromptVersion,
    SwingAnalysisResult,
    SwingSession,
    User,
    UserProfile,
)
from tests.constants import (
    DEMO_PRIORITY_ISSUE,
    DEMO_USER_GOAL,
    DEMO_USER_NAME,
)


@dataclass(frozen=True)
class SeedContext:
    user_id: int
    swing_session_id: int
    conversation_id: int


def seed_minimal_dataset(db: Session) -> SeedContext:
    """Insert a minimal coherent dataset for API and workflow tests."""
    user = User(
        name=DEMO_USER_NAME,
        email="riley@example.com",
        level="intermediate",
        dominant_hand="right",
    )
    db.add(user)
    db.flush()

    db.add(
        UserProfile(
            user_id=user.id,
            goal=DEMO_USER_GOAL,
            golfer_type="fast upper-body rotation golfer",
            current_main_issue=DEMO_PRIORITY_ISSUE,
            preferred_feedback_style="simple and actionable",
            profile_summary="Demo profile for automated tests.",
        )
    )

    swing = SwingSession(
        user_id=user.id,
        club_type="Driver",
        view_type="Front",
        concern="Slice",
        score=72,
        main_issue=DEMO_PRIORITY_ISSUE,
    )
    db.add(swing)
    db.flush()

    db.add(
        SwingAnalysisResult(
            swing_session_id=swing.id,
            phase_summary_json={"phases": []},
            pose_metrics_json={
                "shoulder_rotation_speed": 68,
                "hip_rotation_timing": 72,
                "knee_stability": 85,
                "swing_tempo": 70,
                "wrist_angle_at_impact": 61,
            },
            diagnosis_text="Upper body opens early in the downswing.",
            priority_issue=DEMO_PRIORITY_ISSUE,
            recommended_action="Lower-body lead drill",
        )
    )

    db.add(
        LongTermMemory(
            user_id=user.id,
            memory_type="swing_issue",
            content=DEMO_PRIORITY_ISSUE,
            source_type="test",
            confidence=0.9,
        )
    )

    db.add(
        PromptVersion(
            name="coaching_system",
            version="v0.3",
            template="demo",
            is_active=True,
        )
    )

    conversation = Conversation(user_id=user.id, title="Test", status="active")
    db.add(conversation)
    db.commit()

    return SeedContext(
        user_id=user.id,
        swing_session_id=swing.id,
        conversation_id=conversation.id,
    )

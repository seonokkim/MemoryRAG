"""Seed demo user, swings, knowledge, memories, and prompt versions."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.data.knowledge_seed import KNOWLEDGE_DOCS
from app.models import (
    KnowledgeDocument,
    LongTermMemory,
    PromptVersion,
    SwingAnalysisResult,
    SwingSession,
    User,
    UserProfile,
)
from app.rag.knowledge_index import KnowledgeIndexService

PHASES = {
    "phases": [
        {"name": "Address", "status": "stable"},
        {"name": "Backswing", "status": "stable"},
        {"name": "Top", "status": "caution"},
        {"name": "Downswing", "status": "needs_work"},
        {"name": "Impact", "status": "needs_work"},
        {"name": "Follow", "status": "caution"},
    ]
}

SCORES = [68, 72, 70, 75, 78]
SEED_EMAIL = "riley@example.com"


def _print_summary(db, user_id: int) -> None:
    swings = db.scalar(
        select(func.count()).select_from(SwingSession).where(SwingSession.user_id == user_id)
    )
    memories = db.scalar(
        select(func.count())
        .select_from(LongTermMemory)
        .where(LongTermMemory.user_id == user_id)
    )
    docs = db.scalar(select(func.count()).select_from(KnowledgeDocument))
    print("Seed summary:")
    print(f"  user_id={user_id} (Riley)")
    print(f"  swing_sessions={swings}")
    print(f"  long_term_memories={memories}")
    print(f"  knowledge_documents={docs}")
    print("  prompt_version=coaching_system v0.3 (active)")
    print("API examples: GET /api/users/1/profile  POST /api/coach/chat")


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == SEED_EMAIL).first()
        if existing:
            _print_summary(db, existing.id)
            print("\nSeed skipped: Riley already exists. Clean slate: python scripts/reset_db.py")
            return

        user = User(
            name="Riley",
            email=SEED_EMAIL,
            level="intermediate",
            dominant_hand="right",
        )
        db.add(user)
        db.flush()

        db.add(
            UserProfile(
                user_id=user.id,
                goal="reduce slice",
                golfer_type="fast upper-body rotation golfer",
                current_main_issue="early upper-body opening before impact",
                preferred_feedback_style="simple and actionable",
                profile_summary=(
                    "Direction can vary, but swing tempo is relatively stable. "
                    "Recurring early upper-body opening before impact."
                ),
            )
        )

        for i, score in enumerate(SCORES, start=1):
            session = SwingSession(
                user_id=user.id,
                club_type="Driver",
                view_type="Front",
                concern="Slice",
                video_url=f"file://data/uploads/sample_swing_{i}.mp4",
                score=score,
                main_issue="Early upper-body opening before impact",
            )
            db.add(session)
            db.flush()
            db.add(
                SwingAnalysisResult(
                    swing_session_id=session.id,
                    phase_summary_json=PHASES,
                    pose_metrics_json={
                        "shoulder_rotation_speed": 68,
                        "hip_rotation_timing": 72,
                        "knee_stability": 85,
                        "swing_tempo": 70 + i,
                        "wrist_angle_at_impact": 61,
                    },
                    diagnosis_text="Upper body opens quickly early in the downswing.",
                    evidence_text="Shoulder rotation timing is faster than hip lead in recent sessions.",
                    priority_issue="Early upper-body opening before impact",
                    recommended_action="Lower-body lead drill · 10 minutes",
                )
            )

        for mtype, content, conf in [
            ("swing_issue", "User repeatedly opens upper body early during downswing.", 0.92),
            ("user_goal", "User wants to reduce slice with driver.", 0.88),
            ("preference", "User prefers simple, actionable feedback.", 0.8),
        ]:
            db.add(
                LongTermMemory(
                    user_id=user.id,
                    memory_type=mtype,
                    content=content,
                    source_type="seed",
                    confidence=conf,
                )
            )

        db.add(
            PromptVersion(
                name="coaching_system",
                version="v0.3",
                template="Structured coaching with guardrails and RAG sources.",
                is_active=True,
            )
        )

        knowledge = KnowledgeIndexService(db)
        ingested = 0
        for doc in KNOWLEDGE_DOCS:
            exists = db.scalar(
                select(KnowledgeDocument.id).where(KnowledgeDocument.title == doc["title"])
            )
            if exists:
                continue
            knowledge.ingest_document(
                title=doc["title"],
                content=doc["content"],
                category=doc["category"],
                source="seed",
            )
            ingested += 1

        db.commit()
        print("Seed completed successfully.")
        _print_summary(db, user.id)
        if ingested:
            print(f"  knowledge_documents_ingested={ingested}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

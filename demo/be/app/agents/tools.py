"""Controlled LangChain tool definitions for coach workflow (allowlist-driven)."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.rag.knowledge_index import KnowledgeIndexService
from app.repositories.swing_repository import SwingRepository
from app.repositories.user_repository import UserRepository

TOOL_ALLOWLISTS: dict[str, list[str]] = {
    "progress_check": ["get_recent_swings", "compare_swing_history"],
    "general_golf_knowledge": ["search_golf_knowledge"],
    "golfer_profile": ["get_user_profile", "get_long_term_memories"],
    "swing_diagnosis": [
        "get_recent_swings",
        "search_golf_knowledge",
        "get_long_term_memories",
    ],
    "practice_recommendation": ["search_golf_knowledge", "get_recent_swings"],
    "unclear": [],
}


def _get_user_profile_impl(db: Session, user_id: int) -> dict[str, Any]:
    repo = UserRepository(db)
    user = repo.get_user_with_profile(user_id)
    if not user:
        return {}
    profile = user.profile
    return {
        "user_id": user.id,
        "name": user.name,
        "level": user.level,
        "goal": profile.goal if profile else None,
        "golfer_type": profile.golfer_type if profile else None,
        "current_main_issue": profile.current_main_issue if profile else None,
    }


def _get_recent_swings_impl(db: Session, user_id: int, limit: int = 5) -> list[dict[str, Any]]:
    repo = SwingRepository(db)
    sessions = repo.list_recent(user_id, limit=limit)
    return [
        {
            "id": s.id,
            "score": s.score,
            "main_issue": s.main_issue,
            "club_type": s.club_type,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]


def _search_golf_knowledge_impl(db: Session, query: str) -> list[dict[str, Any]]:
    index = KnowledgeIndexService(db)
    chunks = index.query(query, top_k=5)
    return [
        {"content": c.content, "score": c.score, "metadata": c.metadata} for c in chunks
    ]


def _get_long_term_memories_impl(db: Session, user_id: int, query: str = "") -> list[dict[str, Any]]:
    repo = UserRepository(db)
    memories = repo.list_active_memories(user_id, limit=20)
    rows = [
        {
            "memory_type": m.memory_type,
            "content": m.content,
            "confidence": m.confidence,
        }
        for m in memories
    ]
    if query:
        q = query.lower()
        rows = [r for r in rows if q in r["content"].lower()]
    return rows[:10]


def _compare_swing_history_impl(db: Session, user_id: int, period: str = "recent") -> dict[str, Any]:
    swings = _get_recent_swings_impl(db, user_id, limit=10)
    scores = [s["score"] for s in swings if s.get("score") is not None]
    if not scores:
        return {"period": period, "swing_count": 0, "trend": "no_data"}
    return {
        "period": period,
        "swing_count": len(scores),
        "latest_score": scores[0],
        "average_score": round(sum(scores) / len(scores), 1),
        "trend": "improving" if len(scores) >= 2 and scores[0] >= scores[-1] else "mixed",
    }


TOOL_RUNNERS: dict[str, Any] = {
    "get_user_profile": lambda db, user_id, **kw: _get_user_profile_impl(db, user_id),
    "get_recent_swings": lambda db, user_id, **kw: _get_recent_swings_impl(
        db, user_id, limit=int(kw.get("limit", 5))
    ),
    "search_golf_knowledge": lambda db, user_id, **kw: _search_golf_knowledge_impl(
        db, str(kw.get("query") or "")
    ),
    "get_long_term_memories": lambda db, user_id, **kw: _get_long_term_memories_impl(
        db, user_id, query=str(kw.get("query") or "")
    ),
    "compare_swing_history": lambda db, user_id, **kw: _compare_swing_history_impl(
        db, user_id, period=str(kw.get("period") or "recent")
    ),
}


@tool
def get_user_profile(user_id: int) -> dict:
    """Fetch golfer profile for a user."""
    return {"user_id": user_id}


@tool
def get_recent_swings(user_id: int, limit: int = 5) -> list:
    """Fetch recent swing sessions for a user."""
    return []


@tool
def search_golf_knowledge(query: str) -> list:
    """Search golf knowledge chunks by query."""
    return []


@tool
def get_long_term_memories(user_id: int, query: str = "") -> list:
    """Fetch active long-term memories for a user."""
    return []


@tool
def compare_swing_history(user_id: int, period: str = "recent") -> dict:
    """Compare recent swing scores and trend."""
    return {}


LANGCHAIN_TOOLS = [
    get_user_profile,
    get_recent_swings,
    search_golf_knowledge,
    get_long_term_memories,
    compare_swing_history,
]


def run_allowed_tools(
    db: Session,
    *,
    user_id: int,
    question_type: str,
    query: str,
) -> dict[str, Any]:
    """Execute allowlisted tools for a question type; returns name -> result."""
    allowed = TOOL_ALLOWLISTS.get(question_type, [])
    results: dict[str, Any] = {}
    kwargs = {"query": query, "limit": 5, "period": "recent"}
    for name in allowed:
        runner = TOOL_RUNNERS.get(name)
        if not runner:
            continue
        results[name] = runner(db, user_id, **kwargs)
    return results

from unittest.mock import patch

from app.graph.workflow import run_coach_workflow
from app.llm.mock_client import MockLLMClient
from app.models import Conversation
from app.schemas.coach import StructuredCoachingOutput
from tests.constants import COACH_SLICE_MESSAGE


class TestQualityLoop:
    def test_retry_then_pass(self, db_session, user_id: int) -> None:
        conversation = Conversation(user_id=user_id, title="Retry", status="active")
        db_session.add(conversation)
        db_session.commit()

        bad = StructuredCoachingOutput(summary="", cause="", fix="", confidence=0.1)
        good = StructuredCoachingOutput(
            summary="Slice diagnosis",
            cause="Open clubface",
            fix="Close face at impact",
            recommended_drill="Gate drill",
            confidence=0.85,
            sources=["swing_history"],
        )
        with patch.object(
            MockLLMClient,
            "generate_structured_answer_sync",
            side_effect=[bad, bad, good],
        ):
            result = run_coach_workflow(
                db_session,
                MockLLMClient(),
                user_id=user_id,
                conversation_id=conversation.id,
                user_message=COACH_SLICE_MESSAGE,
                trace_id="quality-retry",
            )

        assert result.get("quality_status") in {"pass", None}
        trace = result.get("trace") or {}
        assert "evaluate_answer" in trace
        assert result.get("retry_count", 0) >= 1 or "rewrite_query" in trace

    def test_fallback_after_max_retries(self, db_session, user_id: int) -> None:
        conversation = Conversation(user_id=user_id, title="Fallback", status="active")
        db_session.add(conversation)
        db_session.commit()

        bad = StructuredCoachingOutput(summary="", cause="", fix="", confidence=0.1)
        with patch.object(
            MockLLMClient,
            "generate_structured_answer_sync",
            return_value=bad,
        ):
            result = run_coach_workflow(
                db_session,
                MockLLMClient(),
                user_id=user_id,
                conversation_id=conversation.id,
                user_message=COACH_SLICE_MESSAGE,
                trace_id="quality-fallback",
            )

        assert result.get("quality_status") == "fallback" or result.get("guardrail_status") == "fallback"
        assert "fallback_answer" in (result.get("trace") or {})
        assert result.get("final_answer")

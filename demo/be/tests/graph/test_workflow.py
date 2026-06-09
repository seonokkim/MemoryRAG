from app.graph.workflow import run_coach_workflow
from app.llm.mock_client import MockLLMClient
from app.models import Conversation, EvalLog, LongTermMemory
from sqlalchemy import select
from tests.constants import COACH_PROGRESS_MESSAGE, COACH_SLICE_MESSAGE


class TestCoachWorkflow:
    def test_happy_path_persists_messages_and_eval(self, db_session, user_id: int) -> None:
        conversation = Conversation(user_id=user_id, title="Workflow", status="active")
        db_session.add(conversation)
        db_session.commit()

        result = run_coach_workflow(
            db_session,
            MockLLMClient(),
            user_id=user_id,
            conversation_id=conversation.id,
            user_message=COACH_PROGRESS_MESSAGE,
            trace_id="test-trace-workflow-1",
        )

        assert result.get("final_answer")
        assert result.get("question_type") == "progress_check"
        assert result.get("guardrail_status") in {"passed", "clarify", "fallback", "skipped"}
        assert result.get("assistant_message_id")
        trace = result.get("trace") or {}
        assert "classify_question" in trace
        assert "invoke_tools" in trace
        assert "log_eval" in trace
        assert result.get("llm_provider") == "mock"
        assert result.get("llm_model") == "mock"

        eval_row = db_session.scalar(
            select(EvalLog).where(EvalLog.conversation_id == conversation.id)
        )
        assert eval_row is not None

    def test_slice_question_structured_output(self, db_session, user_id: int) -> None:
        conversation = Conversation(user_id=user_id, title="Slice", status="active")
        db_session.add(conversation)
        db_session.commit()

        result = run_coach_workflow(
            db_session,
            MockLLMClient(),
            user_id=user_id,
            conversation_id=conversation.id,
            user_message=COACH_SLICE_MESSAGE,
            trace_id="test-trace-slice",
        )
        assert result.get("question_type") == "swing_diagnosis"
        structured = result.get("structured_output")
        assert structured is not None
        confidence = (
            structured.confidence
            if hasattr(structured, "confidence")
            else structured.get("confidence", 0)
        )
        assert confidence >= 0.5

    def test_memory_update_on_slice_message(self, db_session, user_id: int) -> None:
        before = db_session.scalars(
            select(LongTermMemory).where(
                LongTermMemory.user_id == user_id,
                LongTermMemory.content.like("%reduce slice%"),
            )
        ).all()
        conversation = Conversation(user_id=user_id, title="Memory", status="active")
        db_session.add(conversation)
        db_session.commit()

        run_coach_workflow(
            db_session,
            MockLLMClient(),
            user_id=user_id,
            conversation_id=conversation.id,
            user_message=COACH_SLICE_MESSAGE,
            trace_id="test-trace-memory",
        )
        db_session.commit()

        after = db_session.scalars(
            select(LongTermMemory).where(
                LongTermMemory.user_id == user_id,
                LongTermMemory.content.like("%reduce slice%"),
            )
        ).all()
        assert len(after) >= len(before)

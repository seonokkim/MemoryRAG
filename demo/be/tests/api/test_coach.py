from tests.constants import API_PREFIX, COACH_SLICE_MESSAGE
from tests.helpers.http import post_json


class TestCoachApi:
    def test_chat_returns_structured_answer(self, client, user_id: int) -> None:
        body = post_json(
            client,
            f"{API_PREFIX}/coach/chat",
            {"user_id": user_id, "message": COACH_SLICE_MESSAGE},
        )
        assert body["answer"]
        assert body["conversation_id"] > 0
        assert body["message_id"] > 0
        assert body["structured_output"]["summary"]
        assert body["structured_output"]["confidence"] > 0
        assert body["trace_id"]
        assert body["guardrail_status"] in {"passed", "clarify", "fallback", "skipped"}

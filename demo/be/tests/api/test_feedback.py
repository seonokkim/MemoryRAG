from tests.constants import API_PREFIX, COACH_SLICE_MESSAGE
from tests.helpers.http import post_json


class TestFeedbackApi:
    def test_submit_helpful_feedback(self, client, user_id: int) -> None:
        chat = post_json(
            client,
            f"{API_PREFIX}/coach/chat",
            {"user_id": user_id, "message": COACH_SLICE_MESSAGE},
        )
        body = post_json(
            client,
            f"{API_PREFIX}/feedback",
            {
                "user_id": user_id,
                "message_id": chat["message_id"],
                "feedback_type": "helpful",
            },
        )
        assert body["id"] > 0
        assert body["status"] == "saved"

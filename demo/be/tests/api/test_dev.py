from tests.constants import API_PREFIX, COACH_SLICE_MESSAGE
from tests.helpers.http import get_json, post_json


class TestDevApi:
    def test_prompt_versions(self, client, seed) -> None:
        versions = get_json(client, f"{API_PREFIX}/dev/prompt-versions")
        assert len(versions) >= 1
        assert any(v["version"] == "v0.3" for v in versions)

    def test_conversation_trace_after_chat(self, client, user_id: int, seed) -> None:
        chat = post_json(
            client,
            f"{API_PREFIX}/coach/chat",
            {"user_id": user_id, "message": COACH_SLICE_MESSAGE},
        )
        trace = get_json(
            client,
            f"{API_PREFIX}/dev/conversations/{chat['conversation_id']}/trace",
        )
        assert trace["conversation_id"] == chat["conversation_id"]
        assert trace["workflow"] == "coach_chat"

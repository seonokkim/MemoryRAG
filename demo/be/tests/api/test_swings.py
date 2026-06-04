from tests.constants import API_PREFIX, DEMO_PRIORITY_ISSUE
from tests.helpers.http import get_json, post_json


class TestSwingsApi:
    def test_list_sessions(self, client, user_id: int) -> None:
        data = get_json(client, f"{API_PREFIX}/users/{user_id}/swing-sessions")
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_analysis(self, client, swing_session_id: int) -> None:
        data = get_json(client, f"{API_PREFIX}/swing-sessions/{swing_session_id}/analysis")
        assert data["priority_issue"] == DEMO_PRIORITY_ISSUE
        assert data["pose_metrics"]["swing_tempo"] == 70

    def test_create_mock_session(self, client, user_id: int) -> None:
        session = post_json(
            client,
            f"{API_PREFIX}/users/{user_id}/swing-sessions",
            {"club_type": "Driver", "view_type": "Front", "concern": "Slice"},
        )
        assert session["id"] > 0
        analysis = get_json(
            client, f"{API_PREFIX}/swing-sessions/{session['id']}/analysis"
        )
        assert analysis["priority_issue"] == DEMO_PRIORITY_ISSUE

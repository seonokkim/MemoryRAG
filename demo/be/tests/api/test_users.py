from tests.constants import API_PREFIX, DEMO_USER_GOAL, DEMO_USER_NAME
from tests.helpers.http import get_json


class TestUsersApi:
    def test_get_profile(self, client, user_id: int) -> None:
        data = get_json(client, f"{API_PREFIX}/users/{user_id}/profile")
        assert data["name"] == DEMO_USER_NAME
        assert data["goal"] == DEMO_USER_GOAL
        assert data["memory_summary"]

from tests.constants import API_PREFIX
from tests.helpers.http import get_json


class TestHealthApi:
    def test_returns_ok_status(self, client) -> None:
        body = get_json(client, f"{API_PREFIX}/health")
        assert body["status"] == "ok"
        assert body["service"] == "MemoryRAG-be"
        assert "version" in body
        assert "environment" in body

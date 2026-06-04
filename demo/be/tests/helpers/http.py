from typing import Any

from fastapi.testclient import TestClient


def assert_ok(response, *, expected_status: int = 200) -> None:
    assert response.status_code == expected_status, response.text


def get_json(client: TestClient, path: str, *, expected_status: int = 200) -> dict[str, Any]:
    response = client.get(path)
    assert_ok(response, expected_status=expected_status)
    return response.json()


def post_json(
    client: TestClient,
    path: str,
    payload: dict[str, Any],
    *,
    expected_status: int = 200,
) -> dict[str, Any]:
    response = client.post(path, json=payload)
    assert_ok(response, expected_status=expected_status)
    return response.json()

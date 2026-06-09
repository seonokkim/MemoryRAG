#!/usr/bin/env python3
"""Manual smoke test for Gemini coach chat (requires DB + seed)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx

BASE = "http://localhost:8000/api"
MESSAGE = "Why do I keep slicing my driver?"


def main() -> int:
    payload = {"user_id": 1, "message": MESSAGE}
    try:
        response = httpx.post(f"{BASE}/coach/chat", json=payload, timeout=120.0)
    except httpx.ConnectError:
        print("ERROR: API not running at http://localhost:8000")
        return 1

    print(f"Status: {response.status_code}")
    try:
        body = response.json()
    except json.JSONDecodeError:
        print(response.text)
        return 1

    print(json.dumps(body, indent=2))
    if response.status_code != 200:
        return 1
    if not body.get("structured_output", {}).get("summary"):
        print("ERROR: missing structured_output.summary")
        return 1
    print("OK: coach chat smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

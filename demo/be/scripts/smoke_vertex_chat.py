"""
Manual smoke test for real Vertex Gemini coach chat.

Prerequisites:
  pip install -r requirements-optional.txt
  .env: LLM_PROVIDER=vertex, VERTEX_PROJECT_ID=<gcp-project>
  GOOGLE_APPLICATION_CREDENTIALS or gcloud auth application-default login
  API running: uvicorn app.main:app --reload (from demo/be)
  Seed data: python scripts/seed_demo_data.py

Usage (from demo/be):
  python scripts/smoke_vertex_chat.py
  python scripts/smoke_vertex_chat.py --base-url http://localhost:8000 --user-id 1
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _check_env() -> None:
    provider = os.getenv("LLM_PROVIDER", "mock")
    project = (os.getenv("VERTEX_PROJECT_ID") or "").strip()
    if provider != "vertex":
        print("Set LLM_PROVIDER=vertex in .env before running this script.", file=sys.stderr)
        sys.exit(1)
    if not project:
        print("Set VERTEX_PROJECT_ID in .env before running this script.", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke POST /api/coach/chat with Vertex LLM")
    parser.add_argument("--base-url", default=os.getenv("API_BASE_URL", "http://localhost:8000"))
    parser.add_argument("--user-id", type=int, default=int(os.getenv("DEMO_USER_ID", "1")))
    parser.add_argument(
        "--message",
        default="Why do I keep slicing with my driver?",
    )
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

    _check_env()

    url = f"{args.base_url.rstrip('/')}/api/coach/chat"
    payload = {
        "user_id": args.user_id,
        "conversation_id": None,
        "message": args.message,
    }
    print(f"POST {url}")
    print(f"payload: {payload}")

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=payload)
        print(f"status: {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        print("trace_id:", data.get("trace_id"))
        print("latency_ms:", data.get("latency_ms"))
        structured = data.get("structured_output") or {}
        print("summary:", structured.get("summary", data.get("answer", ""))[:200])
        print("confidence:", structured.get("confidence"))


if __name__ == "__main__":
    main()

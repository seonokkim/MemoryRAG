#!/usr/bin/env bash
# Run LangGraph Studio for the memory-rag coach workflow (from demo/be).
#
# WSL2 + Windows browser: localhost:2024 in WSL is NOT reachable from the browser.
# Use --tunnel (auto on WSL) so Studio gets a public baseUrl.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH=.

EXTRA_ARGS=()
if [[ "${STUDIO_TUNNEL:-}" == "1" ]] || grep -qi microsoft /proc/version 2>/dev/null; then
  echo "WSL detected — starting with --tunnel (Windows browser cannot reach WSL 127.0.0.1)"
  EXTRA_ARGS+=(--tunnel)
fi

exec .venv/bin/langgraph dev \
  --config langgraph.json \
  --studio-url https://apac.smith.langchain.com \
  --no-browser \
  "${EXTRA_ARGS[@]}" \
  "$@"

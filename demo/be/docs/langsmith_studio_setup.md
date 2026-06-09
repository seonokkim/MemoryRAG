# LangSmith APAC tracing & LangGraph Studio (local)

Optional observability for the existing **16-node** coach workflow in `app/graph/workflow.py`.  
Not required for the FE demo flow — see [fe_integration.md](fe_integration.md).  
FastAPI remains the production entrypoint; Studio is for local graph inspection only.

## One API key for tracing and Studio

Use **the same** `LANGSMITH_API_KEY` in `demo/be/.env` for:

| Tool | How it reads the key |
|------|----------------------|
| **FastAPI** (`uvicorn`) | `configure_langsmith()` on startup → `LANGSMITH_*` env |
| **LangGraph Studio** (`langgraph dev`) | `langgraph.json` → `"env": ".env"` |

No separate Studio key. One PAT, one project, one APAC endpoint.

If a key was ever exposed (e.g. screenshot), **revoke it in LangSmith UI** and paste the new PAT into `.env` once — then use that single key everywhere.

## Environment variables

Copy from `.env.example` and set in `demo/be/.env` (never commit real keys):

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<your_apac_pat>
LANGSMITH_PROJECT=memory-rag-demo
LANGSMITH_ENDPOINT=https://apac.api.smith.langchain.com
```

`configure_langsmith()` in `app/core/observability.py` mirrors these to `LANGCHAIN_*` when tracing is on.  
Prefer **`LANGSMITH_*`** only in `.env`; legacy aliases are optional.

**APAC UI:** https://apac.smith.langchain.com  
**APAC API:** https://apac.api.smith.langchain.com

Do **not** set `LANGSMITH_WORKSPACE_ID` unless your key is org-scoped and LangSmith docs require it.

## FastAPI + LangSmith tracing

```bash
cd demo/be
source .venv/bin/activate
export PYTHONPATH=.

# MySQL (required for coach chat)
cd infra/docker && docker compose up -d && cd ../..

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Startup log should include:

```text
LangSmith tracing enabled: project=memory-rag-demo endpoint=https://apac.api.smith.langchain.com
```

Restart the server after any `.env` change.

## Smoke test checklist

### 1. Health

```bash
curl http://localhost:8000/api/health
```

Expected: `200` with `"status":"ok"`.

### 2. Coach chat (generates LangSmith trace)

```bash
curl -X POST http://localhost:8000/api/coach/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"message":"trace test: why do I keep slicing my driver?"}'
```

Expected:

- HTTP `200`
- `structured_output.summary` present
- `conversation_id` and `trace_id` in response

### 3. Dev trace API

```bash
curl http://localhost:8000/api/dev/conversations/<conversation_id>/trace
```

Expected:

- `llm_provider`, `llm_model`
- `workflow`: `coach_chat`
- Nested `trace` with node steps (`load_context`, `generate_answer`, …)

### 4. LangSmith APAC UI

1. Open https://apac.smith.langchain.com
2. Go to **Tracing** (not **Monitor**)
3. Project: `memory-rag-demo`
4. Find run name: `memory-rag-coach-workflow`

Monitor stays empty until enough trace volume exists.

## LangGraph Studio (optional)

### Install CLI

```bash
cd demo/be
source .venv/bin/activate
pip install -U "langgraph-cli[inmem]"
```

Optional: add to `requirements-optional.txt` for team installs.

### Studio entrypoint

| File | Role |
|------|------|
| `langgraph.json` | CLI config — graph `memory_rag_coach` |
| `app/graph/studio.py` | Exports compiled `graph` via `build_coach_workflow()` |

### Run Studio (APAC)

```bash
cd demo/be
source .venv/bin/activate
export PYTHONPATH=.
langgraph dev --config langgraph.json --studio-url https://apac.smith.langchain.com
# or: ./scripts/run_studio.sh
```

Select graph **`memory_rag_coach`** in Studio (not a default template).

See [langgraph_studio_setup.md](langgraph_studio_setup.md) for full 16-node workflow details.

MySQL must be running with seed data (`user_id=1`).

### Studio sample input

Use `STUDIO_SAMPLE_INPUT` from `app/graph/studio.py` or:

```json
{
  "user_id": 1,
  "conversation_id": 1,
  "user_message": "Why do I keep slicing my driver?",
  "trace_id": "studio-dev",
  "latency_ms": 0,
  "prompt_version": "v0.3",
  "trace": {"trace_id": "studio-dev"},
  "retrieved_chunk_count": 0,
  "retry_count": 0
}
```

## Troubleshooting

### Trace ingest returns 403

1. Confirm project exists in **APAC** UI: `memory-rag-demo`
2. Confirm `.env` has `LANGSMITH_ENDPOINT=https://apac.api.smith.langchain.com`
3. Regenerate API key from APAC workspace (Settings → API Keys)
4. Restart FastAPI after `.env` changes
5. Remove/comment `LANGSMITH_WORKSPACE_ID` unless required for org-scoped keys
6. Check **Tracing**, not Monitor

### Port 8000 already in use

```bash
fuser -k 8000/tcp   # Linux
# or stop the old uvicorn process, then start one clean instance
```

### Coach chat returns 500

- Start MySQL: `cd demo/be/infra/docker` → copy `.env.example` to `.env` → `docker compose up -d`
- Run seed: `python scripts/seed_demo_data.py`

### pytest must not use live keys

Tests force `LLM_PROVIDER=mock` and `LANGSMITH_TRACING=false` via `tests/fixtures/environment.py`.

```bash
cd demo/be
export PYTHONPATH=.
pytest
```

## Related code

- `app/core/observability.py` — env wiring for LangSmith
- `app/main.py` — calls `configure_langsmith()` on startup
- `app/graph/workflow.py` — `build_coach_workflow()`, `run_coach_workflow()`

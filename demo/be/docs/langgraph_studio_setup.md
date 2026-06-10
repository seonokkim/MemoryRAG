# LangGraph Studio — memory-rag coach workflow (16 nodes)

Visualize and debug the **existing** coach graph (`build_coach_workflow` in `app/graph/workflow.py`).  
This is **not** a template `model → tools` graph. Optional — not required for the FE demo; see [fe_integration.md](fe_integration.md).

## Prerequisites

- Run all commands from **`demo/be`** (not repo root)
- MySQL via Docker + seed data
- APAC LangSmith PAT in `.env` (same key for Tracing and Studio)

## Environment (`.env`)

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://apac.api.smith.langchain.com
LANGSMITH_PROJECT=memory-rag-demo
LANGSMITH_API_KEY=<your_apac_pat>

LLM_PROVIDER=gemini_api
GEMINI_MODEL=gemini-flash-latest
VECTOR_STORE_PROVIDER=none
DATABASE_URL=mysql+pymysql://memory_rag:memory_rag@localhost:3306/memory_rag

ENABLE_QUALITY_LOOP=true
ENABLE_AGENT_TOOLS=true
QUALITY_MAX_RETRIES=2
QUALITY_CONFIDENCE_THRESHOLD=0.5
```

**Important:** Do **not** set empty `LANGCHAIN_TRACING_V2=` in `.env` — it breaks `langgraph dev`.  
`configure_langsmith()` sets `LANGCHAIN_*` mirrors when the app or `studio.py` loads.

| URL | Purpose |
|-----|---------|
| `https://apac.api.smith.langchain.com` | API / trace ingest (`LANGSMITH_ENDPOINT`) |
| `https://apac.smith.langchain.com` | Studio UI (`--studio-url`) |

## Full stack setup

```bash
cd demo/be/infra/docker
docker compose up -d
cd ../..

source .venv/bin/activate
export PYTHONPATH=.
alembic upgrade head
python scripts/seed_demo_data.py
```

## Install Studio CLI

```bash
cd demo/be
source .venv/bin/activate
pip install -U "langgraph-cli[inmem]"
```

## Run LangGraph Studio

```bash
cd demo/be
source .venv/bin/activate
export PYTHONPATH=.
./scripts/run_studio.sh
```

**WSL2 + Windows browser:** `./scripts/run_studio.sh` auto-enables `--tunnel` because `http://127.0.0.1:2024` inside WSL is **not** reachable from a Windows browser. The terminal prints a Studio URL like:

```text
https://apac.smith.langchain.com/studio/?baseUrl=https://xxxx.trycloudflare.com
```

Open **that exact URL** from the terminal — do not use `baseUrl=http://127.0.0.1:2024` on WSL.

Force tunnel on any OS: `STUDIO_TUNNEL=1 ./scripts/run_studio.sh`

In Studio, select graph: **`memory_rag_coach`**

Expected nodes (16):

```text
load_context → classify_question → retrieve_profile → retrieve_swing_history
→ retrieve_memory → retrieve_knowledge → invoke_tools → generate_answer
→ validate_output → evaluate_answer → (guardrail | rewrite_query | fallback_answer)
→ save_messages → (update_memory | log_eval) → log_eval
```

## Studio sample input

```json
{
  "user_id": 1,
  "conversation_id": 1,
  "user_message": "Why do I keep slicing my driver?",
  "messages": [],
  "trace_id": "studio-dev",
  "latency_ms": 0,
  "prompt_version": "v0.3",
  "trace": {"trace_id": "studio-dev"},
  "retrieved_chunk_count": 0,
  "retry_count": 0
}
```

Also available as `STUDIO_SAMPLE_INPUT` in `app/graph/studio.py`.

## FastAPI (optional, separate terminal)

Studio does not replace FastAPI. For HTTP API testing:

```bash
cd demo/be
source .venv/bin/activate
export PYTHONPATH=.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Use port **8000** for FastAPI and port **2024** (default) for `langgraph dev`.

## Troubleshooting

### `Unable to connect` / `Failed to fetch` (WSL)

**Cause:** Browser on Windows tries `http://127.0.0.1:2024` (Windows localhost), but `langgraph dev` runs inside WSL.

**Fix:**

```bash
cd demo/be
source .venv/bin/activate
export PYTHONPATH=.
./scripts/run_studio.sh
```

Copy the **Studio UI** line from the terminal (with `trycloudflare.com` baseUrl when tunnel is on).  
Also ensure `langgraph` runs via `.venv/bin/langgraph` or activated venv — `langgraph: command not found` means the server never started.

### `domain is not allowed` (tunnel / Configure connection)

LangSmith blocks unknown Agent Server domains until you **allowlist** them (security).

1. Open https://apac.smith.langchain.com/studio/
2. Click **Configure connection** (or **Connect to a local server**)
3. **Base URL:** paste the tunnel from terminal, e.g. `https://xxxx.trycloudflare.com`
4. Expand **Advanced Settings** → **Allowed origins / Allowed list**
5. Add the **same** tunnel URL (or domain `xxxx.trycloudflare.com`)
6. Click **Connect**
7. Select graph **`memory_rag_coach`**

Do not skip step 4–5 — pasting only the Studio URL in the address bar is not enough.

### Studio shows only `model → tools`

1. Run from **`demo/be`**, not repo root
2. Pass **`--config langgraph.json`**
3. Confirm `langgraph.json` points to `./app/graph/studio.py:graph`
4. Select graph **`memory_rag_coach`** in Studio dropdown
5. Restart `langgraph dev` and refresh Studio

### `langgraph dev` crashes on startup

- Remove empty `LANGCHAIN_TRACING_V2=` from `.env`
- Set `export PYTHONPATH=.`
- Ensure MySQL is running

### Graph import / DB errors

- `docker compose up -d` in `infra/docker`
- `python scripts/seed_demo_data.py`
- Check `DATABASE_URL` in `.env`

### LangSmith auth / wrong region

- `LANGSMITH_ENDPOINT=https://apac.api.smith.langchain.com`
- `--studio-url https://apac.smith.langchain.com`
- `LANGSMITH_PROJECT=memory-rag-demo`

## Files

| File | Role |
|------|------|
| `langgraph.json` | CLI config — graph id `memory_rag_coach` |
| `app/graph/studio.py` | Exports `graph` via `build_coach_workflow()` |
| `app/graph/workflow.py` | Source of truth for workflow (unchanged) |

See also: [langsmith_studio_setup.md](langsmith_studio_setup.md) for tracing smoke tests.

# Frontend integration (connected)

The React app (`demo/fe`) calls the local FastAPI backend for the main demo flow. Some screens still use inline mocks when the API is unreachable; **AI Coach does not** — it requires a live backend response.

## Prerequisites

1. **MySQL** (Docker Compose) + migrate + seed — demo user **Riley**, `user_id=1`
2. **Backend** at `http://localhost:8000` — `./scripts/run_local.sh` (bash/WSL) or `.\scripts\run_local.ps1` (Windows)
3. **Frontend env** (optional) — create `demo/fe/.env.local` if you need to override defaults

## Environment

**Dev default:** leave `VITE_API_BASE_URL` unset — Vite proxies `/api` → `http://127.0.0.1:8000` (works on WSL2 + Windows browser).

```env
VITE_DEMO_USER_ID=1
# Optional — only if not using Vite dev proxy:
# VITE_API_BASE_URL=http://localhost:8000
```

## API client

| File | Role |
|------|------|
| `src/app/api/client.ts` | `fetch` wrapper + endpoint helpers |
| `src/app/api/types.ts` | Minimal TypeScript types for BE responses |

Dev default: same-origin `/api` via Vite proxy. Production / direct API: set `VITE_API_BASE_URL=http://localhost:8000`.

## Connected screens

| FE route | Component | BE APIs |
|----------|-----------|---------|
| `/` | HomeScreen | `GET /api/users/{id}/profile`, `GET /api/users/{id}/swing-sessions` |
| `/upload` | SwingUploadScreen | `POST /api/users/{id}/swing-sessions` → navigate `/analysis?sessionId=` |
| `/analysis` | AnalysisResultScreen | `GET /api/swing-sessions/{id}/analysis` |
| `/coach` | AIChatScreen | `POST /api/coach/chat`, `POST /api/feedback` |
| `/dev` | DevPanelScreen | `GET /api/dev/prompt-versions`, optional `GET /api/dev/conversations/{id}/trace` |

`conversation_id` from coach chat is stored in `sessionStorage` (`demo_conversation_id`) for Dev trace.

**Coach screen:** shows `LIVE API` when the backend is reachable. On failure, the UI displays an API error — **no mock coaching fallback**.

## Still mock / fallback

| Screen | Notes |
|--------|--------|
| GolferProfileScreen | Inline mock |
| PracticeRoutineScreen | Inline mock |
| MonthlyReportScreen | Inline mock |
| Home charts | Mock metrics if API fails; scores from BE when available |
| DevPanel | Trace + prompt versions from API; empty state until coach chat in session |

## Local demo flow

```bash
# 1. MySQL (copy infra/docker/.env.example → .env first; set local passwords)
cd demo/be/infra/docker && docker compose up -d

# 2. Migrate + seed
cd demo/be
source .venv/bin/activate   # or .\.venv\Scripts\activate on Windows
export PYTHONPATH=.
alembic upgrade head
python scripts/seed_demo_data.py

# 3. Backend
./scripts/run_local.sh      # or .\scripts\run_local.ps1
# → http://localhost:8000/docs

# 4. Frontend
cd demo/fe && pnpm install && pnpm dev
# → http://localhost:5173
```

Walkthrough: Home → Upload → Analysis → Coach (`Why do I keep slicing?`) → Feedback → Dev panel.

## Coach chat request

```json
POST /api/coach/chat
{
  "user_id": 1,
  "conversation_id": null,
  "message": "Why do I keep slicing?"
}
```

Response: `answer`, `structured_output`, `sources`, `latency_ms`, `conversation_id`, `message_id`.

## External services

| Service | Required for FE flow? | Notes |
|---------|----------------------|-------|
| MySQL (Docker Compose) | **Yes** | Local DB; Cloud SQL only for GCP deploy |
| FastAPI backend | **Yes** | Port `8000` |
| LLM provider | **For coach replies** | See below |
| GCP / Vertex / GCS | No | Production path — [manual_setup_later.md](manual_setup_later.md) |
| Chroma / OpenAI | No | Optional; default `VECTOR_STORE_PROVIDER=none` |
| LangSmith | No | Optional tracing — [langsmith_studio_setup.md](langsmith_studio_setup.md) |

**LLM for coach (`demo/be/.env`):**

| `LLM_PROVIDER` | API key? | Use case |
|----------------|----------|----------|
| `mock` (`.env.example` default) | None | API wiring, pytest, offline smoke |
| `gemini_api` | `GEMINI_API_KEY` | Real Gemini answers; recommended for demo + E2E. `pip install -r requirements-optional.txt`. No GCP project. |
| `vertex` | GCP auth + `VERTEX_PROJECT_ID` | Production Gemini via Vertex AI |
| `openai` | `OPENAI_API_KEY` | Optional alternative |

GCP (Vertex), OpenAI, Chroma, and GCS are **not** required for the local FE ↔ BE flow. For a realistic coach demo, set `LLM_PROVIDER=gemini_api` and a `GEMINI_API_KEY`.

## E2E (live stack)

| Command | What it checks |
|---------|----------------|
| `cd demo/fe && pnpm test:e2e:stack` | Node script: Vite proxy → FastAPI → MySQL → coach chat (no browser) |
| `cd demo/fe && pnpm test:e2e` | Playwright: `/coach` UI, `LIVE API` badge, real reply |

Both expect backend on `:8000` and frontend dev server on `:5173`. Coach E2E assumes `LLM_PROVIDER=gemini_api` with a valid `GEMINI_API_KEY` (or another non-mock provider that returns structured answers).

## Troubleshooting

| Issue | Check |
|-------|--------|
| CORS error | Only when bypassing Vite proxy — set `CORS_ORIGINS` to include `http://localhost:5173` |
| Empty home | Seed ran; `VITE_DEMO_USER_ID=1` |
| Coach `OFFLINE` / API error | BE on `:8000`; MySQL up; if `gemini_api`, check `GEMINI_API_KEY` |
| E2E coach timeout | Gemini cold start — allow up to 120s; confirm `structured_output.summary` in API response |
| No Dev trace | Send at least one coach message first |

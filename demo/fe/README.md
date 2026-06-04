# MemoryRAG frontend (demo)

Mobile-style React/Vite PoC for the AI swing coach demo. **Main flow is wired to the local backend**; some screens still use inline mocks as fallback.

## Setup

```powershell
cd demo/fe
pnpm install
pnpm dev
```

Optional overrides: create `.env.local` with `VITE_API_BASE_URL` and `VITE_DEMO_USER_ID` (defaults match [../../README.md](../../README.md)).

Open http://localhost:5173 (backend must run at http://localhost:8000).

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | FastAPI base URL |
| `VITE_DEMO_USER_ID` | `1` | Seed user Riley |

## Connected vs mock

**Connected:** Home, Upload, Analysis, AI Coach, Dev (prompt versions + trace)

**Mock fallback:** Profile detail charts, Routine, Monthly Report, partial Dev workflow/RAG tabs

API client: `src/app/api/client.ts` · backend: [demo/be/README.md](../be/README.md)

## Scripts

- `pnpm dev` — local dev server
- `pnpm build` — production build check

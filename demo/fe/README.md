# memory-rag frontend (demo)

Mobile-style React/Vite UI for the AI swing coach demo. Main flows call the local FastAPI backend; Profile, Routine, and Monthly Report use static demo content.

## Setup

```bash
cd demo/fe
pnpm install
pnpm dev
```

Open http://localhost:5173 (backend must run at http://localhost:8000).

**Dev:** Vite proxies `/api` → `http://127.0.0.1:8000`. Coach chat uses the live API only — no mock replies on failure.

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_BASE_URL` | *(unset in dev)* | Override API base; dev uses Vite proxy |
| `VITE_DEMO_USER_ID` | `1` | Seed user Riley |

Optional: create `.env.local` with the overrides above.

## Connected vs static screens

**API-backed:** Home, Upload, Analysis, AI Coach, Dev panel (trace + prompt versions)

**Static demo data:** Profile, Routine, Monthly Report

See [../be/docs/fe_integration.md](../be/docs/fe_integration.md).

## Scripts

- `pnpm dev` — local dev server
- `pnpm build` — production build check
- `pnpm test:e2e:stack` — live E2E via Vite proxy (BE + FE must be running)
- `pnpm test:e2e` — Playwright browser E2E (needs `playwright install-deps` on Linux)

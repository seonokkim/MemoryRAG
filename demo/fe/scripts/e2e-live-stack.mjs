#!/usr/bin/env node
/**
 * Live stack E2E (no browser): Vite proxy /api → FastAPI coach workflow.
 *
 * Prerequisites:
 *   1. Backend: cd demo/be && uvicorn app.main:app --host 0.0.0.0 --port 8000
 *   2. Frontend: cd demo/fe && pnpm dev   (or set FE_BASE_URL to running Vite)
 */

const BE_BASE = (process.env.BE_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const FE_BASE = (process.env.FE_BASE_URL ?? "http://127.0.0.1:5173").replace(/\/$/, "");
const COACH_MESSAGE = "Why do I keep slicing my driver?";
const TIMEOUT_MS = 120_000;

async function fetchJson(url, init) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(url, { ...init, signal: controller.signal });
    const text = await res.text();
    let body = null;
    if (text) {
      try {
        body = JSON.parse(text);
      } catch {
        body = text;
      }
    }
    return { ok: res.ok, status: res.status, body };
  } finally {
    clearTimeout(timer);
  }
}

function fail(msg) {
  console.error(`FAIL: ${msg}`);
  process.exit(1);
}

function pass(msg) {
  console.log(`OK: ${msg}`);
}

async function main() {
  console.log(`BE ${BE_BASE}  FE ${FE_BASE}`);

  const beHealth = await fetchJson(`${BE_BASE}/api/health`);
  if (!beHealth.ok || beHealth.body?.status !== "ok") {
    fail(`Backend health ${beHealth.status} — start uvicorn on :8000`);
  }
  pass(`Backend health (${beHealth.body.service} ${beHealth.body.version})`);

  const feHealth = await fetchJson(`${FE_BASE}/api/health`);
  if (!feHealth.ok || feHealth.body?.status !== "ok") {
    fail(
      `Vite proxy health ${feHealth.status} — run 'pnpm dev' in demo/fe (proxies /api → :8000)`
    );
  }
  pass("Vite proxy /api/health → backend");

  const profile = await fetchJson(`${FE_BASE}/api/users/1/profile`);
  if (!profile.ok || profile.body?.name !== "Riley") {
    fail(`Profile via proxy failed (${profile.status})`);
  }
  pass(`Profile via proxy (user=${profile.body.name})`);

  console.log(`POST /api/coach/chat (may take up to ${TIMEOUT_MS / 1000}s)…`);
  const chat = await fetchJson(`${FE_BASE}/api/coach/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ user_id: 1, message: COACH_MESSAGE }),
  });

  if (!chat.ok) {
    fail(`Coach chat ${chat.status}: ${JSON.stringify(chat.body)}`);
  }

  const { conversation_id, message_id, answer, structured_output } = chat.body ?? {};
  if (!conversation_id || !message_id || !answer) {
    fail(`Invalid coach response: ${JSON.stringify(chat.body)}`);
  }
  if (!structured_output?.summary) {
    fail("Missing structured_output.summary from coach workflow");
  }

  pass(`Coach chat via FE proxy (conversation=${conversation_id}, message=${message_id})`);
  pass(`Answer preview: ${String(answer).slice(0, 80)}…`);
  console.log("\nLive stack E2E passed (FE proxy → FastAPI).");
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});

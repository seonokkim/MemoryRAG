# Manual setup (later — not required for local MVP)

The backend runs fully in **local/mock mode** without any of the steps below.

Use this checklist when moving to GCP production or optional cloud LLM/vector providers.

## Not needed for local development

- GCP Project creation
- Billing account linking
- Service Account key download
- Vertex AI API enablement
- Vertex AI Vector Search index / endpoint / deployed index creation
- Cloud SQL instance provisioning
- Cloud Run deployment
- Secret Manager secret creation
- GCS bucket creation
- OpenAI API key issuance
- GKE cluster creation
- Qdrant Cloud or any third-party vector SaaS signup
- LangSmith account (local MVP runs with `LANGSMITH_TRACING=false`)

## Optional LangSmith tracing (after local E2E passes)

LangGraph is already the workflow engine. LangSmith adds optional trace UI for debugging and evaluation.

1. Create account at https://smith.langchain.com  
2. Create API key  
3. Add to `.env`:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=memory-rag-local
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

4. Restart BE, run `POST /api/coach/chat`  
5. Confirm trace in LangSmith project (`memory-rag-coach-workflow`)

MySQL `eval_logs` and `GET /api/dev/conversations/{id}/trace` remain the local observability path.

## Needed after local verification (GCP production path)

1. **GCP Project** with billing enabled  
2. **APIs:** Cloud Run, Cloud SQL Admin, Artifact Registry, Cloud Build, Secret Manager, Cloud Storage, Vertex AI  
3. **Cloud SQL for MySQL** — database `memory_rag`, user credentials  
4. **Alembic migrate** against Cloud SQL (Auth Proxy or CI job)  
5. **Artifact Registry** + container build (`infra/docker/Dockerfile`)  
6. **Cloud Run** deploy with env from `infra/gcp/env.example.yaml`  
7. **Secret Manager:** `DATABASE_URL`, optional `OPENAI_API_KEY`, Vertex Vector Search IDs  
8. **Vertex AI Gemini** — `LLM_PROVIDER=vertex`, `VERTEX_PROJECT_ID`  
9. **Vertex AI Vector Search** — `VECTOR_STORE_PROVIDER=vertex` + index/endpoint/deployed index IDs  
10. **Cloud Logging** — `ENABLE_CLOUD_LOGGING=true`  
11. **GCS** (optional) — `GCS_BUCKET_NAME` for swing video assets  
12. **GKE** (optional) — only if you need worker separation or GPU/batch jobs  

## Real LLM demo (Vertex Gemini, no vector index yet)

1. `pip install -r requirements-optional.txt`  
2. Enable Vertex AI API on your GCP project  
3. `.env`:

```env
LLM_PROVIDER=vertex
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_LOCATION=us-central1
VERTEX_MODEL_NAME=gemini-1.5-flash
VECTOR_STORE_PROVIDER=none
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=memory-rag-local
```

4. Start BE + `python scripts/smoke_vertex_chat.py`  
5. Later: `VECTOR_STORE_PROVIDER=vertex` + Matching Engine IDs  

## Real LLM demo (Gemini API — no GCP)

Recommended for live coach demo and FE E2E before Vertex/GCP setup.

1. `pip install -r requirements-optional.txt`  
2. `.env`:

```env
LLM_PROVIDER=gemini_api
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-flash-latest
VECTOR_STORE_PROVIDER=none
```

3. Start BE + `python scripts/smoke_gemini_chat.py`  
4. FE: `cd demo/fe && pnpm dev` → Coach screen should show `LIVE API`

Uses the Google AI Gemini API directly — no GCP project, service account, or Vertex enablement.

## Optional local enhancements (still no GCP)

```bash
pip install -r requirements-optional.txt
```

- `VECTOR_STORE_PROVIDER=chroma` — local LlamaIndex + Chroma vectors  
- `LLM_PROVIDER=openai` — requires `OPENAI_API_KEY`  
- `LANGSMITH_TRACING=true` — requires `LANGSMITH_API_KEY` (optional observability)  

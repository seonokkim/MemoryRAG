# Interface and implementation policy

Local mode must run without external keys. Production providers are selected through interfaces and environment variables.

## 1. Architecture principles

- **MySQL** is the source of truth for users, swings, conversations, memories, and knowledge chunks.
- **LangGraph** orchestrates the coach workflow; nodes are small and testable.
- **LlamaIndex-oriented retrievers** handle RAG; local default uses SQL keyword fallback only.
- **FastAPI** exposes HTTP; routes delegate to services, never to provider concrete classes.

## 2. Interface-first design

Business logic depends on abstractions (`BaseLLMClient`, `VectorStoreBackend`, `BaseStorageService`), not vendor SDKs. Optional providers are wired through factories and environment variables.

## 3. Python naming convention

| Use | Avoid |
|-----|-------|
| `BaseXxx` (ABC) | `IXxx` |
| `XxxBackend` / `XxxProvider` | `XxxImpl` |
| `MockLLMClient`, `ChromaVectorStore`, `LocalStorageService` | Java/C# style prefixes |

## 4. LLM provider interface

**Module:** `app/llm/`

| Role | Type |
|------|------|
| Contract | `BaseLLMClient` |
| Local default | `MockLLMClient` |
| Real LLM PoC (no GCP) | `GeminiAPIClient` (`LLM_PROVIDER=gemini_api`) |
| GCP production target | `VertexAIClient` |
| Optional | `OpenAIClient` |
| Selection | `get_llm_client(settings)` in `app/llm/factory.py` |

**Methods (sync for LangGraph; async delegates to sync on base):**

- `classify_question_sync` / `classify_question`
- `generate_structured_answer_sync` / `generate_structured_answer`
- `extract_memory_sync` / `extract_memory`

**Factory policy:**

- `LLM_PROVIDER=mock` → `MockLLMClient` (no keys)
- `LLM_PROVIDER=gemini_api` → lazy import `GeminiAPIClient` (requires `GEMINI_API_KEY`)
- `LLM_PROVIDER=vertex` → lazy import `VertexAIClient`
- `LLM_PROVIDER=openai` → lazy import `OpenAIClient`
- Unknown provider → `ValueError`

API routes and graph nodes must not instantiate `VertexAIClient` or `OpenAIClient` directly.

## 5. Vector store backend interface

**Module:** `app/rag/vector_store/`

| Role | Type |
|------|------|
| Contract | `VectorStoreBackend` |
| Local default (`none`) | `SqlFallbackVectorStore` |
| Optional local | `ChromaVectorStore` |
| GCP production skeleton | `VertexVectorSearchStore` |
| Selection | `get_vector_store(settings)` |

**Methods:** `provider_name`, `is_available()`, `upsert()`, `search()`

**Data types:** `VectorRecord`, `VectorSearchHit` (dataclasses in `base.py`)

**Factory policy:**

- `VECTOR_STORE_PROVIDER=none` → SQL fallback only; no Chroma/Vertex/GCP imports
- `VECTOR_STORE_PROVIDER=chroma` → lazy import Chroma; clear unavailable if deps missing
- `VECTOR_STORE_PROVIDER=vertex` → lazy import Vertex; unavailable until index/endpoint IDs set
- Vector search failure in retrievers → SQL fallback

## 6. Storage abstraction

**Module:** `app/storage/`

| Role | Type |
|------|------|
| Contract | `BaseStorageService` |
| Local default | `LocalStorageService` |
| GCP target | `GCSStorageService` (falls back to local on error) |
| Selection | `get_storage_service(settings)` |

Local MVP uses `file://` URLs under `data/uploads`. GCS is optional via `GCS_BUCKET_NAME`.

## 7. Repository / service boundary

```text
api → services
services → repositories / graph / rag / llm / storage
repositories → models
graph nodes → repositories / rag / llm (via BaseLLMClient)
rag → VectorStoreBackend (factory)
```

**Forbidden:**

- Repositories importing FastAPI request/response types
- Models importing services or repositories
- API routes importing Vertex/OpenAI/Chroma concrete classes
- Graph nodes importing provider concrete classes
- Eager import of GCP/OpenAI/Chroma when `mock` + `none` are selected

## 8. LangGraph node responsibility

| Category | Nodes |
|----------|-------|
| Context load | `load_context` |
| Retrieval only | `retrieve_profile`, `retrieve_swing_history`, `retrieve_memory`, `retrieve_knowledge` |
| Classification | `classify_question` |
| Generation | `generate_answer` (LLM only) |
| Validation | `validate_output`, `guardrail` |
| Persistence | `save_messages`, `update_memory`, `log_eval` |

Each node: input `CoachState`, return partial state update. Traces append via `trace_utils.py`.

## 9. Memory policy

Long-term memories are stored in MySQL. Extraction runs in `update_memory` when `ENABLE_MEMORY_UPDATE=true`. Mock provider returns deterministic slice-related memories.

## 10. Fallback policy

| Setting | Behavior |
|---------|----------|
| `LLM_PROVIDER=mock` | Always works without keys |
| `VECTOR_STORE_PROVIDER=none` | SQL retrieval only |
| Vector search fails | SQL fallback in retrievers |
| Chroma not installed + `chroma` | `is_available()` false; retriever falls back |
| Vertex env missing + `vertex` | `is_available()` false; retriever falls back |
| Guardrail | Safe coaching answer; avoid over-confident claims |

## 11. Testing policy

Default pytest environment:

```powershell
$env:PYTHONPATH="."
$env:LLM_PROVIDER="mock"
$env:DATABASE_URL="sqlite:///:memory:"
$env:VECTOR_STORE_PROVIDER="none"
pytest -q
```

Factory and import-boundary tests live under `tests/llm/`, `tests/rag/`, and `tests/architecture/`.

## 12. GCP production provider policy

Production targets (manual setup — see `docs/manual_setup_later.md`):

- **LLM:** Vertex AI Gemini via `VertexAIClient`
- **Vector:** Vertex AI Vector Search via `VertexVectorSearchStore`
- **Storage:** GCS via `GCSStorageService`
- **Deploy:** Cloud Run + Cloud SQL (artifacts under `infra/gcp/`)

None of these are required for local development or CI in mock+none mode.

## 13. Optional LangSmith tracing

| Layer | Role |
|-------|------|
| **LangGraph** | Workflow engine (required for coach pipeline) |
| **MySQL `eval_logs` + Dev trace API** | Local SoT for latency, guardrail, workflow trace |
| **LangSmith** | Optional external observability when `LANGSMITH_TRACING=true` |

- Default: `LANGSMITH_TRACING=false` — no `LANGSMITH_API_KEY` required.
- Startup: `configure_langsmith(settings)` in `app/main.py` sets process env only (no mandatory SDK import).
- Missing API key with tracing enabled: warning log, tracing stays off, app continues.
- LangGraph `invoke` config: `run_name=memory-rag-coach-workflow`, `metadata` includes `user_id`, `conversation_id`, providers, `prompt_version`.

LangSmith supplements local logs; it does not replace `trace_utils.py` or `log_eval`.

# GCP deployment (MemoryRAG backend)

## Recommended production path

| Component | GCP service |
|-----------|-------------|
| API | Cloud Run |
| Relational data | Cloud SQL (MySQL) |
| Object storage | Cloud Storage |
| Logs | Cloud Logging |
| LLM | Vertex AI Gemini |
| Vectors | **Vertex AI Vector Search** |

Set `VECTOR_STORE_PROVIDER=vertex` and configure:

- `VERTEX_VECTOR_INDEX_ID`
- `VERTEX_VECTOR_ENDPOINT_ID`
- `VERTEX_VECTOR_DEPLOYED_INDEX_ID`

MySQL remains the source of truth; vector search accelerates retrieval over `knowledge_chunks` and long-term memory.

## Local vs production

- **Local:** `VECTOR_STORE_PROVIDER=none` (SQL fallback) or `chroma` (optional Chroma + LlamaIndex).
- **Production:** `VECTOR_STORE_PROVIDER=vertex` with Matching Engine resources in the same region as Cloud Run.

Vertex Vector Search is optional at runtime — if misconfigured, the API falls back to MySQL retrieval and still starts.

## Cloud Build / Run

See `cloudbuild.yaml`, `cloud-run.yaml`, and `env.example.yaml`.

## Terraform

`terraform/` provides Artifact Registry and GCS skeleton; extend for Cloud SQL, Vector Search index/endpoint, and IAM.

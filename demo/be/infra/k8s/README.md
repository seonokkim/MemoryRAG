# GKE (optional production path)

Cloud Run is recommended for the MVP API surface. Use GKE when you need:

- Separate worker pools for ingestion or future pose/video inference
- Fine-grained autoscaling and multi-service mesh
- Long-running background jobs

Apply manifests:

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.example.yaml  # copy and fill values first
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
```

Point `DB_HOST` to Cloud SQL via private IP or the Cloud SQL Auth Proxy sidecar.

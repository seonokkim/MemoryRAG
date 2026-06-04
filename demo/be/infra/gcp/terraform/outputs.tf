output "artifact_registry" {
  value = google_artifact_registry_repository.be.id
}

output "gcs_bucket" {
  value = google_storage_bucket.swing_assets.url
}

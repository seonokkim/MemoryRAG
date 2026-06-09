variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "artifact_repo" {
  type    = string
  default = "memory-rag"
}

variable "gcs_bucket_name" {
  type        = string
  description = "Globally unique bucket name for swing assets"
}

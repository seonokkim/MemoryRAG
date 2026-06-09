terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_artifact_registry_repository" "be" {
  location      = var.region
  repository_id = var.artifact_repo
  format        = "DOCKER"
  description   = "memory-rag backend images"
}

resource "google_storage_bucket" "swing_assets" {
  name     = var.gcs_bucket_name
  location = var.region
  uniform_bucket_level_access = true
}

from pathlib import Path

from app.core.config import Settings
from app.storage.base import BaseStorageService
from app.storage.local_storage import LocalStorageService


class GCSStorageService(BaseStorageService):
    """
    GCS-backed storage when bucket is configured.
    Falls back to local disk when credentials or upload fail.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._local = LocalStorageService()

    def resolve_video_url(self, filename: str | None) -> str | None:
        if not filename:
            return None
        bucket = self.settings.gcs_bucket_name
        if bucket:
            return f"gs://{bucket}/swings/{filename}"
        return self._local.resolve_video_url(filename)

    def store_bytes(self, path: str, data: bytes) -> str:
        bucket = self.settings.gcs_bucket_name
        if bucket:
            try:
                from google.cloud import storage

                client = storage.Client()
                blob = client.bucket(bucket).blob(path)
                blob.upload_from_string(data)
                return f"gs://{bucket}/{path}"
            except Exception:
                pass
        return self._local.store_bytes(path, data)

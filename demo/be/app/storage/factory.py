from app.core.config import Settings, get_settings
from app.storage.base import BaseStorageService
from app.storage.gcs_storage import GCSStorageService
from app.storage.local_storage import LocalStorageService


def get_storage_service(settings: Settings | None = None) -> BaseStorageService:
    cfg = settings or get_settings()
    if cfg.gcs_bucket_name:
        return GCSStorageService(cfg)
    return LocalStorageService()

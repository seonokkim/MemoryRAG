from pathlib import Path

from app.storage.base import BaseStorageService


class LocalStorageService(BaseStorageService):
    """Local file URLs for MVP; no GCS credentials required."""

    def __init__(self, upload_root: str = "data/uploads") -> None:
        self.upload_root = Path(upload_root)

    def resolve_video_url(self, filename: str | None) -> str | None:
        if not filename:
            return None
        local = self.upload_root / filename
        return f"file://{local.resolve()}"

    def store_bytes(self, path: str, data: bytes) -> str:
        target = self.upload_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return str(target.resolve())

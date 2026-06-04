from abc import ABC, abstractmethod


class BaseStorageService(ABC):
    """Object storage abstraction for swing videos and uploads."""

    @abstractmethod
    def resolve_video_url(self, filename: str | None) -> str | None:
        ...

    @abstractmethod
    def store_bytes(self, path: str, data: bytes) -> str:
        ...

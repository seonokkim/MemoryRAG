"""LlamaIndex + Chroma helpers (optional; only used when VECTOR_STORE_PROVIDER=chroma)."""

from pathlib import Path

from app.core.config import get_settings


def get_chroma_persist_dir() -> Path:
    settings = get_settings()
    path = Path(settings.chroma_persist_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_llama_index_available() -> bool:
    try:
        import llama_index.core  # noqa: F401

        return True
    except ImportError:
        return False

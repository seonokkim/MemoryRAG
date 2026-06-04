import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any

from app.core.config import Settings, get_settings

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)

_session_log_file: Path | None = None
_logging_signature: str | None = None


def _be_root() -> Path:
    return Path(__file__).resolve().parents[2]


def create_log_file_path(log_dir: str) -> Path:
    """Create demo/be/logs/YYYYMMDD_HHMMSS.log (directory created if missing)."""
    directory = _be_root() / log_dir
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return directory / f"{stamp}.log"


def get_session_log_file() -> Path | None:
    """Path for the current process session log file, if file logging is enabled."""
    return _session_log_file


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        rid = request_id_ctx.get()
        if rid:
            payload["request_id"] = rid
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            payload.update(record.extra_fields)
        return json.dumps(payload, ensure_ascii=False)


class RequestContextFormatter(logging.Formatter):
    """Readable console/file format with optional request_id from context."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        rid = request_id_ctx.get()
        if rid:
            return f"{message} [request_id={rid}]"
        return message


def _build_text_formatter() -> logging.Formatter:
    return RequestContextFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _build_formatter(settings: Settings) -> logging.Formatter:
    if settings.log_json:
        return JsonFormatter(datefmt="%Y-%m-%d %H:%M:%S")
    return _build_text_formatter()


def configure_logging(settings: Settings | None = None) -> None:
    global _session_log_file, _logging_signature

    cfg = settings or get_settings()
    signature = (
        f"{cfg.app_env}:{cfg.enable_cloud_logging}:{cfg.log_json}:"
        f"{cfg.file_logging_enabled}:{cfg.log_dir}"
    )
    root = logging.getLogger()
    if _logging_signature == signature and root.handlers:
        return

    root.handlers.clear()
    root.setLevel(logging.INFO)
    _session_log_file = None

    if cfg.enable_cloud_logging:
        try:
            import google.cloud.logging

            client = google.cloud.logging.Client()
            client.setup_logging()
            _logging_signature = signature
            return
        except Exception:
            root.warning("Cloud Logging unavailable; falling back to console")

    formatter = _build_formatter(cfg)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    if cfg.file_logging_enabled:
        log_path = create_log_file_path(cfg.log_dir)
        _session_log_file = log_path
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
        logging.getLogger(__name__).info("Session log file: %s", log_path)

    _logging_signature = signature


def log_event(logger: logging.Logger, message: str, **fields: Any) -> None:
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        "",
        0,
        message,
        (),
        None,
    )
    record.extra_fields = fields  # type: ignore[attr-defined]
    logger.handle(record)

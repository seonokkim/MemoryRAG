import logging
import re
import types
from datetime import datetime
from pathlib import Path

import pytest

from app.core.config import Settings
from app.core.logging import (
    configure_logging,
    create_log_file_path,
    get_session_log_file,
)


class TestLoggingFile:
    def test_create_log_file_path_format(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr("app.core.logging._be_root", lambda: tmp_path)
        fixed = datetime(2026, 6, 4, 21, 30, 15)
        monkeypatch.setattr(
            "app.core.logging.datetime",
            types.SimpleNamespace(now=lambda tz=None: fixed, strftime=datetime.strftime),
        )

        path = create_log_file_path("logs")
        assert path.name == "20260604_213015.log"
        assert path.parent == tmp_path / "logs"
        assert path.parent.is_dir()

    def test_file_logging_creates_logs_dir(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr("app.core.logging._be_root", lambda: tmp_path)
        monkeypatch.setattr(
            "app.core.logging._logging_signature",
            None,
        )

        configure_logging(
            Settings(
                app_env="local",
                log_to_file=True,
                log_dir="logs",
                enable_cloud_logging=False,
            )
        )

        session_file = get_session_log_file()
        assert session_file is not None
        assert session_file.parent == tmp_path / "logs"
        assert session_file.exists()

    def test_log_to_file_false_stdout_only(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr("app.core.logging._be_root", lambda: tmp_path)
        monkeypatch.setattr("app.core.logging._logging_signature", None)

        configure_logging(
            Settings(
                app_env="local",
                log_to_file=False,
                enable_cloud_logging=False,
            )
        )

        assert get_session_log_file() is None
        root = logging.getLogger()
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0], logging.StreamHandler)

    def test_prod_disables_file_logging(self) -> None:
        settings = Settings(app_env="prod", log_to_file=True)
        assert settings.file_logging_enabled is False

    def test_cloud_logging_disables_file_logging(self) -> None:
        settings = Settings(enable_cloud_logging=True, log_to_file=True)
        assert settings.file_logging_enabled is False

    def test_app_import_with_log_to_file_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LOG_TO_FILE", "false")
        monkeypatch.setenv("LLM_PROVIDER", "mock")
        monkeypatch.setenv("VECTOR_STORE_PROVIDER", "none")

        from app.core.config import get_settings
        from app.main import create_app

        get_settings.cache_clear()
        assert create_app() is not None

    def test_timestamp_filename_regex(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr("app.core.logging._be_root", lambda: tmp_path)
        path = create_log_file_path("logs")
        assert re.fullmatch(r"\d{8}_\d{6}\.log", path.name)

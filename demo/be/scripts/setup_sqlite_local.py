"""Create SQLite schema via SQLAlchemy models (no Alembic) and seed demo data.

Use when MySQL/Docker is unavailable (e.g. WSL without Docker Desktop):

  export DATABASE_URL=sqlite:///./data/local.db
  export PYTHONPATH=.
  python scripts/setup_sqlite_local.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings
from app.core.database import Base, get_engine, reset_engine
import app.models  # noqa: F401 — register tables on Base.metadata

from scripts.seed_demo_data import seed


def main() -> None:
    get_settings.cache_clear()
    reset_engine()
    settings = get_settings()
    if not settings.sqlalchemy_database_url.startswith("sqlite"):
        print("ERROR: DATABASE_URL must be sqlite for this helper.")
        raise SystemExit(1)
    Base.metadata.create_all(get_engine())
    seed()
    print(f"\nSQLite ready at {settings.sqlalchemy_database_url}")


if __name__ == "__main__":
    main()

"""Drop and recreate all tables via Alembic downgrade/upgrade."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run([sys.executable, "-m", "alembic", "downgrade", "base"], cwd=ROOT, check=False)
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()

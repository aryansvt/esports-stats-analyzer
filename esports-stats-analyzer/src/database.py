from __future__ import annotations
import sqlite3
from pathlib import Path

from .config import DB_PATH


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    target = db_path or DB_PATH
    if not target.exists():
        raise FileNotFoundError(
            f'SQLite database not found at {target}. Run scripts/build_database.py first.'
        )
    return sqlite3.connect(target)

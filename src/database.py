import sqlite3
from pathlib import Path
from typing import Optional


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target = db_path
    if target is None:
        from .config import DB_PATH
        target = DB_PATH

    if not target.exists():
        raise FileNotFoundError(
            f"SQLite database not found at {target}. Run scripts/build_database.py first."
        )

    return sqlite3.connect(target)
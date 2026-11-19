"""The Lost and Found Desk's database: where the file is, how a connection is opened, the
migrations, and get_db, the dependency that gives every request its own connection. Ready to use.
"""

import sqlite3
from collections.abc import Iterator
from pathlib import Path

# The database file, beside this file. The tests never touch it: they use a throwaway file.
DATABASE_PATH = Path(__file__).parent / "lost_and_found.db"

# The numbered migration scripts: 0001_create_items.sql, 0002_create_claims.sql.
MIGRATIONS = Path(__file__).parent / "migrations"


def open_db(path: Path | str) -> sqlite3.Connection:
    """Opens the database file at path, with rows that read by column name and foreign keys on."""
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate(conn: sqlite3.Connection) -> list[int]:
    """Runs, in order, every migration script the database hasn't had yet, and returns their
    numbers, such as [1, 2], or [] when the database is up to date."""
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    ran = []
    for path in sorted(MIGRATIONS.glob("*.sql")):
        number = int(path.name[:4])
        if number > version:
            conn.executescript(path.read_text(encoding="utf-8"))
            # PRAGMA takes no placeholders. number comes from our own file name, never a request.
            conn.execute(f"PRAGMA user_version = {number}")
            conn.commit()
            ran.append(number)
    return ran


def get_db() -> Iterator[sqlite3.Connection]:
    """Gives each request its own connection: commits when the route works, rolls back when it
    raises an error, and always closes it."""
    conn = open_db(DATABASE_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

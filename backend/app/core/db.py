"""
Database layer (SQLite).

SQLite is a full SQL database that lives in a single file — no server to run,
perfect for development and small apps. It's built into Python (the `sqlite3`
module), so there's nothing extra to install.

We open a fresh connection per operation. SQLite handles concurrent access with
file locking, and this avoids the "SQLite objects can't be shared across
threads" issue (FastAPI runs sync endpoints in a thread pool).
"""

import sqlite3

from app.core.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    role        TEXT NOT NULL,          -- 'user' or 'model'
    text        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
"""


def get_connection() -> sqlite3.Connection:
    """Open a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # rows accessible by column name
    return conn


def init_db() -> None:
    """Create the tables if they don't exist yet. Safe to call on every startup."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)

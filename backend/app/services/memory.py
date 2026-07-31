"""
Conversation memory — now backed by the SQLite database (Milestone 11).

The PUBLIC INTERFACE is identical to the old in-memory version
(get_history / add_message / reset), so nothing else in the app changed when we
switched from a RAM dict to a real database. That's the payoff of keeping all
history access behind these three functions.

Difference from before: conversations now PERSIST. Restart the server and the
history is still there, because it lives in a file on disk, not in RAM.
"""

from app.core.db import get_connection


def get_history(session_id: str) -> list[dict]:
    """Return the list of past messages for a session, oldest first."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, text FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
    return [{"role": row["role"], "text": row["text"]} for row in rows]


def add_message(session_id: str, role: str, text: str) -> None:
    """Append one message (role = 'user' or 'model') to a session's history."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, text) VALUES (?, ?, ?)",
            (session_id, role, text),
        )
        conn.commit()


def reset(session_id: str) -> None:
    """Delete a single conversation's history from the database."""
    with get_connection() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()

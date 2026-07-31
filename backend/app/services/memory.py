"""
Conversation memory — a simple in-memory store.

This holds the history of every conversation, keyed by session_id:

    {
      "abc-123": [
        {"role": "user",  "text": "My name is Moksha."},
        {"role": "model", "text": "Nice to meet you, Moksha!"},
      ],
      "def-456": [ ... ],
    }

IMPORTANT — this is TEMPORARY memory. It lives in the server's RAM, so:
  - it is lost when the server restarts, and
  - it is not shared if you run multiple server processes.
That is fine for development. In Milestone 11 we swap this for a database so
conversations survive restarts (PERSISTENT memory). Because all history access
goes through these functions, that swap will only touch this one file.
"""

# The store itself: a dict mapping session_id -> list of messages.
# "model" is Gemini's name for the assistant role.
_conversations: dict[str, list[dict]] = {}


def get_history(session_id: str) -> list[dict]:
    """Return the list of past messages for a session (empty if new)."""
    return _conversations.get(session_id, [])


def add_message(session_id: str, role: str, text: str) -> None:
    """Append one message (role = "user" or "model") to a session's history."""
    # setdefault creates an empty list the first time we see this session.
    _conversations.setdefault(session_id, []).append({"role": role, "text": text})


def reset(session_id: str) -> None:
    """Forget a single conversation (used when the user starts a New Chat)."""
    _conversations.pop(session_id, None)

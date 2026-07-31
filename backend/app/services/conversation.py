"""
Conversation engine.

The orchestrator: given a session_id and a user message, it produces the
assistant's reply — now WITH memory of previous turns in that session.

How memory works here (this is the heart of Milestone 6):
  1. Look up the session's past messages from the memory store.
  2. Build the full list [ ...history..., new user message ].
  3. Send that whole list to Gemini, so it can see the conversation.
  4. Save both the user message and the reply back into the store.
"""

from app.services import gemini_service
from app.services import memory

# CONTEXT WINDOW: a model can only "see" a limited amount of text (tokens) at
# once. If a chat ran for hours, replaying ALL of it would eventually overflow
# that limit (and cost more). So we only send the most recent messages. This is
# a crude but effective cap; smarter strategies (summarising old turns) come later.
MAX_HISTORY_MESSAGES = 20


def _to_gemini_contents(messages: list[dict]) -> list[dict]:
    """Convert our simple {role, text} messages into Gemini's turn format."""
    return [
        {"role": m["role"], "parts": [{"text": m["text"]}]}
        for m in messages
    ]


def generate_response(session_id: str, message: str) -> str:
    """
    Turn a user message into a reply, using and updating this session's history.
    """
    # 1. Past turns for this session (empty list if it's a brand-new chat).
    history = memory.get_history(session_id)

    # 2. Full conversation = history + the new user message. We keep only the
    #    last MAX_HISTORY_MESSAGES turns so we never overflow the context window.
    messages = history + [{"role": "user", "text": message}]
    messages = messages[-MAX_HISTORY_MESSAGES:]

    # 3. Ask Gemini using the WHOLE conversation, not just this one line.
    #    (If this raises GeminiError we save nothing, so a failed request never
    #     corrupts the history with a half-turn.)
    reply = gemini_service.generate_reply(_to_gemini_contents(messages))

    # 4. Persist this turn (user + assistant) for next time.
    memory.add_message(session_id, "user", message)
    memory.add_message(session_id, "model", reply)

    return reply

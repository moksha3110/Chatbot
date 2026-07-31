"""
Conversation engine.

The orchestrator: given a session_id and a user message, it produces the
assistant's reply, using and updating this session's memory.

Its job now reads as a clean four-step recipe, because the fiddly work is
delegated:
  - remembering turns          -> memory.py
  - assembling the prompt       -> prompt_builder.py
  - talking to the model        -> gemini_service.py
The engine just coordinates them.
"""

from app.services import gemini_service
from app.services import memory
from app.services import prompt_builder


def generate_response(session_id: str, message: str) -> str:
    """
    Turn a user message into a reply, using and updating this session's history.
    """
    # 1. Past turns for this session (empty list if it's a brand-new chat).
    history = memory.get_history(session_id)

    # 2. Assemble the full prompt (system instruction + history + new message).
    prompt = prompt_builder.build(history, message)

    # 3. Ask Gemini. If this raises GeminiError we save nothing, so a failed
    #    request never corrupts the history with a half-turn.
    reply = gemini_service.generate_reply(
        prompt.contents,
        system_instruction=prompt.system_instruction,
    )

    # 4. Persist this turn (user + assistant) for next time.
    memory.add_message(session_id, "user", message)
    memory.add_message(session_id, "model", reply)

    return reply

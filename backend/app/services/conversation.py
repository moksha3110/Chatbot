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
from app.tools.registry import tool_manager


def generate_response(session_id: str, message: str) -> str:
    """
    Turn a user message into a reply, using and updating this session's history.
    """
    # 1. Past turns for this session (empty list if it's a brand-new chat).
    history = memory.get_history(session_id)

    # 2. Assemble the full prompt (system instruction + history + new message).
    prompt = prompt_builder.build(history, message)

    # 3. Ask Gemini, giving it the available tools. It may call a tool (e.g.
    #    get_current_time) before producing the final answer. If this raises
    #    GeminiError we save nothing, so a failed request never corrupts history.
    reply = gemini_service.generate_reply(
        prompt.contents,
        system_instruction=prompt.system_instruction,
        tools=tool_manager.declarations(),
        execute_tool=tool_manager.execute,
    )

    # 4. Persist this turn (user + assistant) for next time.
    memory.add_message(session_id, "user", message)
    memory.add_message(session_id, "model", reply)

    return reply

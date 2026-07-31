"""
Conversation engine.

This is the ORCHESTRATOR: given a user's message, it produces the assistant's
reply. Right now that job is tiny — it just forwards the message to Gemini.

So why does it exist as its own layer? Because this is the designated home for
everything that will make our bot smart, and those features are next:
  - Milestone 6: conversation HISTORY (remember previous turns)
  - Milestone 7: PROMPT BUILDER (system instructions + history + message)
  - Milestone 8+: TOOL calling (weather, search, RAG, ...)

Keeping the engine separate from both the HTTP layer (routes) and the raw model
call (gemini_service) means each of those additions has an obvious place to go,
without touching the web layer or the SDK wrapper.
"""

from app.services import gemini_service


def generate_response(message: str) -> str:
    """
    Turn a user message into an assistant reply.

    Thin today (a straight pass-through to Gemini). In later milestones this
    is where history and prompt construction will be assembled before calling
    the model.
    """
    return gemini_service.generate_reply(message)

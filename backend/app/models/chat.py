"""
Pydantic models (schemas) for the chat endpoint.

Keeping these in their own file means routes stay short, and other layers
(tests, the conversation engine) can import the same shapes without pulling
in the whole web app.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """The JSON body the client sends to POST /chat."""
    # Validation: reject empty messages and absurdly long ones (min/max length).
    # FastAPI turns a violation into an automatic 422 before our code runs.
    message: str = Field(..., min_length=1, max_length=4000, examples=["Hello, chatbot!"])
    # Which conversation this message belongs to. Optional: if the client
    # doesn't send one (e.g. the very first message), the server creates one
    # and returns it, so the client can reuse it for the rest of the chat.
    session_id: str | None = Field(default=None, examples=["my-session-1"])


class ChatResponse(BaseModel):
    """The JSON body the server returns from POST /chat."""
    response: str
    # Echo back the session id so the client always knows which conversation
    # to continue (especially when the server assigned a new one).
    session_id: str

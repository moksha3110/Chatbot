"""
Pydantic models (schemas) for the chat endpoint.

Keeping these in their own file means routes stay short, and other layers
(tests, the conversation engine) can import the same shapes without pulling
in the whole web app.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """The JSON body the client sends to POST /chat."""
    message: str = Field(..., examples=["Hello, chatbot!"])


class ChatResponse(BaseModel):
    """The JSON body the server returns from POST /chat."""
    response: str

"""
FastAPI backend for the internship chatbot.

Milestone 2: a basic, well-typed backend.
  - GET  /       -> health check (is the server alive?)
  - POST /chat   -> echoes the user's message back (no AI yet)

Both endpoints use Pydantic models so that FastAPI can validate the JSON
coming IN and guarantee the shape of the JSON going OUT.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

# The FastAPI "app" object is the heart of the backend.
# Everything (routes, docs, middleware) attaches to it.
# The title/description/version show up in the auto-generated docs at /docs.
app = FastAPI(
    title="Internship Chatbot API",
    description="Backend for a milestone-by-milestone AI chatbot. Currently echoes messages.",
    version="0.2.0",
)


# ---------------------------------------------------------------------------
# Data models (Pydantic)
# ---------------------------------------------------------------------------
# A Pydantic model is a Python class that describes the SHAPE of some JSON.
# FastAPI uses it to:
#   1. Parse and VALIDATE incoming JSON (reject bad requests automatically).
#   2. Describe the endpoint in the interactive /docs page.

class ChatRequest(BaseModel):
    """The JSON body the client must send to POST /chat."""
    # `message` is required and must be a string.
    # Field(...) lets us attach extra info: `...` means "required",
    # and `examples` pre-fills the value shown in the /docs "Try it out" box.
    message: str = Field(..., examples=["Hello, chatbot!"])


class ChatResponse(BaseModel):
    """The JSON body the server promises to send back from POST /chat."""
    response: str


# ---------------------------------------------------------------------------
# Routes (endpoints)
# ---------------------------------------------------------------------------

@app.get("/")
def home():
    """Health check. Visiting the root URL confirms the server is running."""
    return {"status": "Chatbot backend is running"}


# `response_model=ChatResponse` tells FastAPI the exact shape of the output.
# It documents the response in /docs AND filters the returned data so only
# the declared fields are ever sent to the client.
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Receive a user message and echo it back.

    This echo is a deliberate placeholder. In Milestone 3 we will replace
    the single line below with a real call to the Gemini API.
    """
    reply = f"You said: {request.message}"
    return ChatResponse(response=reply)

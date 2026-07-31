"""
FastAPI backend for the internship chatbot.

Milestone 4: talk to a browser.
  - GET  /       -> health check (is the server alive?)
  - POST /chat   -> sends the message to Gemini and returns its reply
  - CORS enabled so the React frontend (a different origin) may call us.

main.py owns the HTTP layer only. The actual Gemini call lives in
gemini_service.py, so this file stays focused on routing and validation.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import the AI layer. generate_reply() does the Gemini call;
# GeminiError is the single error type we need to handle here.
from gemini_service import generate_reply, GeminiError

# The FastAPI "app" object is the heart of the backend.
# Everything (routes, docs, middleware) attaches to it.
# The title/description/version show up in the auto-generated docs at /docs.
app = FastAPI(
    title="Internship Chatbot API",
    description="Backend for a milestone-by-milestone AI chatbot, powered by Google Gemini.",
    version="0.4.0",
)

# --- CORS (Cross-Origin Resource Sharing) ---------------------------------
# A browser page served from http://localhost:5173 (our React dev server) is a
# DIFFERENT ORIGIN than this API at http://127.0.0.1:8000. By default browsers
# BLOCK such cross-origin requests for security. This middleware tells the
# browser "these origins are allowed to call me", which unblocks the frontend.
# We list only our local dev origins (never use "*" once real users exist).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],   # allow GET, POST, etc.
    allow_headers=["*"],   # allow Content-Type and any other headers
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
    Receive a user message, ask Gemini for a reply, and return it.

    If the Gemini call fails (bad key, quota, network...), we catch the
    GeminiError and return HTTP 502 with a clear message instead of letting
    the server crash with a 500.
    """
    try:
        reply = generate_reply(request.message)
    except GeminiError as e:
        # 502 Bad Gateway = "an upstream service (Gemini) failed."
        raise HTTPException(status_code=502, detail=str(e))

    return ChatResponse(response=reply)

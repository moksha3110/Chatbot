"""
HTTP routes.

An APIRouter is like a mini-app: we declare endpoints on it here, and main.py
plugs it into the real FastAPI app with app.include_router(). This keeps route
definitions out of main.py, which stays focused on assembling the app.

Routes are the HTTP layer only: validate input (via models), call a service,
shape the output. They contain NO Gemini logic — that lives in services.
"""

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services import conversation
from app.services.gemini_service import GeminiError

router = APIRouter()


@router.get("/")
def home():
    """Health check. Confirms the server is running."""
    return {"status": "Chatbot backend is running"}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Receive a user message, ask the conversation engine for a reply, return it.

    The route knows nothing about Gemini — it just calls the engine and
    translates a GeminiError into a clean HTTP 502.
    """
    try:
        reply = conversation.generate_response(request.message)
    except GeminiError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return ChatResponse(response=reply)

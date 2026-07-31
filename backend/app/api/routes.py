"""
HTTP routes.

An APIRouter is like a mini-app: we declare endpoints on it here, and main.py
plugs it into the real FastAPI app with app.include_router(). This keeps route
definitions out of main.py, which stays focused on assembling the app.

Routes are the HTTP layer only: validate input (via models), call a service,
shape the output. They contain NO Gemini logic — that lives in services.
"""

from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.models.chat import ChatRequest, ChatResponse
from app.services import conversation
from app.services.gemini_service import GeminiError
from app.rag import documents, embeddings
from app.rag.vector_store import vector_store

router = APIRouter()


@router.get("/")
def home():
    """Health check. Confirms the server is running."""
    return {"status": "Chatbot backend is running"}


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Receive a user message, ask the conversation engine for a reply, return it.

    A session_id ties messages together into one conversation. If the client
    didn't send one, we mint a fresh id here and return it so the client can
    keep using it for the rest of the chat.
    """
    session_id = request.session_id or str(uuid4())

    try:
        reply = conversation.generate_response(session_id, request.message)
    except GeminiError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return ChatResponse(response=reply, session_id=session_id)


@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF to give the bot knowledge (RAG).

    Pipeline: read the PDF -> extract text -> chunk it -> embed each chunk ->
    store the vectors. After this, /chat automatically retrieves the most
    relevant chunks for each question.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a .pdf file.")

    data = await file.read()
    text = documents.extract_text(data)
    chunks = documents.chunk_text(text)
    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in that PDF (is it a scan?).",
        )

    try:
        vectors = embeddings.embed_texts(chunks)
    except GeminiError as e:
        raise HTTPException(status_code=502, detail=str(e))

    vector_store.add(chunks, vectors)
    return {
        "filename": file.filename,
        "chunks_added": len(chunks),
        "total_chunks": vector_store.count(),
    }

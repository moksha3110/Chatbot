"""
Application entry point (the "app factory").

After the refactor, main.py has ONE job: assemble the app. It creates the
FastAPI instance, wires up CORS, and plugs in the routes. All the actual
logic lives in the other layers (models, services, api).

Run it with:  uvicorn app.main:app --reload   (from the backend/ folder)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router

app = FastAPI(
    title="Internship Chatbot API",
    description="Backend for a milestone-by-milestone AI chatbot, powered by Google Gemini.",
    version="0.9.0",
)

# CORS: allow our React dev origin(s) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Plug the endpoints (GET /, POST /chat) into the app.
app.include_router(router)

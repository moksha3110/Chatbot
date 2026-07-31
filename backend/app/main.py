"""
Application entry point (the "app factory").

After the refactor, main.py has ONE job: assemble the app. It creates the
FastAPI instance, wires up CORS, and plugs in the routes. All the actual
logic lives in the other layers (models, services, api).

Run it with:  uvicorn app.main:app --reload   (from the backend/ folder)
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.db import init_db
from app.core.logging import setup_logging
from app.api.routes import router

# Configure logging and create database tables before serving requests.
setup_logging(settings.LOG_LEVEL)
init_db()

logger = logging.getLogger("app")

app = FastAPI(
    title="Internship Chatbot API",
    description="Backend for a milestone-by-milestone AI chatbot, powered by Google Gemini.",
    version="0.13.0",
)


# Catch-all error handler: log the real error, but return a generic message so
# we never leak internal details (stack traces, file paths) to clients.
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


# CORS: allow our React dev origin(s) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Plug the endpoints (GET /, POST /chat) into the app.
app.include_router(router)

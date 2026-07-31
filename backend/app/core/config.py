"""
Central configuration.

Every setting the app needs is read HERE, in one place, from the environment.
Before this refactor, gemini_service.py read env vars directly. Centralizing
config means: one obvious place to look, and no scattered os.getenv() calls.
"""

import os

from dotenv import load_dotenv

# Read the .env file (KEY=VALUE pairs) into the environment, once, at startup.
load_dotenv()


class Settings:
    """Plain settings object. Simple and explicit — no magic."""

    # --- Gemini ---
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    # --- CORS: which browser origins may call this API ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


# A single shared instance the rest of the app imports: `from app.core.config import settings`
settings = Settings()

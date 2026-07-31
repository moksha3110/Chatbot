"""
Gemini service — the ONLY place that knows how to talk to Google Gemini.

Unchanged in behaviour from Milestone 3; it now reads its configuration from
the central `settings` object instead of calling os.getenv() itself.
"""

from google import genai

from app.core.config import settings


class GeminiError(Exception):
    """Raised when we cannot get a valid reply from Gemini.

    The API layer catches this and turns it into a clean HTTP 502, so a
    failure talking to Gemini never crashes the whole server.
    """


# Fail loudly and early if the key is missing.
if not settings.GEMINI_API_KEY:
    raise GeminiError(
        "GEMINI_API_KEY is not set. Copy backend/.env.example to backend/.env "
        "and add your key from https://aistudio.google.com/apikey"
    )

# Create the Gemini client once, at import time, and reuse it for every request.
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_reply(message: str) -> str:
    """
    Send a single message to Gemini and return the model's text reply.

    Raises GeminiError on any API/network failure or an empty response.
    """
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=message,
        )
    except Exception as e:
        raise GeminiError(f"Gemini request failed: {e}") from e

    if not response.text:
        raise GeminiError("Gemini returned an empty response.")

    return response.text

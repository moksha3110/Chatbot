"""
Gemini service — the ONLY place that knows how to talk to Google Gemini.

Unchanged in behaviour from Milestone 3; it now reads its configuration from
the central `settings` object instead of calling os.getenv() itself.
"""

from google import genai
from google.genai import types

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


def generate_reply(contents, system_instruction: str | None = None) -> str:
    """
    Send `contents` to Gemini and return the model's text reply.

    `contents` may be:
      - a plain string (a single message), or
      - a list of turns in Gemini's format, e.g.
          [{"role": "user",  "parts": [{"text": "hi"}]},
           {"role": "model", "parts": [{"text": "hello"}]}, ...]
    Passing the whole list is how we give the model conversation history.

    `system_instruction` (optional) is a high-priority instruction that sets the
    model's persona and rules. Gemini takes it separately from `contents`, via
    the request config — not as another turn in the conversation.

    Raises GeminiError on any API/network failure or an empty response.
    """
    # Only build a config object when we actually have a system instruction.
    config = (
        types.GenerateContentConfig(system_instruction=system_instruction)
        if system_instruction
        else None
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config=config,
        )
    except Exception as e:
        raise GeminiError(f"Gemini request failed: {e}") from e

    if not response.text:
        raise GeminiError("Gemini returned an empty response.")

    return response.text

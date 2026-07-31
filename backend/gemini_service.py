"""
Gemini service module.

This is the ONLY place in the codebase that knows how to talk to Google Gemini.
Keeping it separate from main.py means:
  - main.py stays focused on HTTP (routes, request/response),
  - if we ever swap Gemini for another model, we change ONE file,
  - the AI logic is easy to test and reason about in isolation.

Public surface: one function -> generate_reply(message) -> str
"""

import os

from dotenv import load_dotenv
from google import genai

# load_dotenv reads the .env file and puts its KEY=VALUE pairs into the
# environment (os.environ). This is how our secret gets into the program
# WITHOUT ever being written in the code.
load_dotenv()

# Read configuration from the environment.
#   GEMINI_API_KEY : required secret (from .env)
#   GEMINI_MODEL   : optional; defaults to a model this account can use.
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")


class GeminiError(Exception):
    """Raised when we cannot get a valid reply from Gemini.

    main.py catches this and turns it into a clean HTTP error, so a failure
    talking to Gemini never crashes the whole server.
    """


# Create the Gemini client once, when this module is first imported, and
# reuse it for every request (creating a client per request would be wasteful).
# If the key is missing we fail LOUDLY and EARLY with a clear message.
if not API_KEY:
    raise GeminiError(
        "GEMINI_API_KEY is not set. Copy backend/.env.example to backend/.env "
        "and add your key from https://aistudio.google.com/apikey"
    )

client = genai.Client(api_key=API_KEY)


def generate_reply(message: str) -> str:
    """
    Send the user's message to Gemini and return the model's text reply.

    Raises GeminiError if the API call fails (bad key, no network, quota, etc.)
    or if Gemini returns an empty response.
    """
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=message,
        )
    except Exception as e:
        # Wrap ANY SDK/network error in our own error type so the rest of the
        # app only has to know about GeminiError, not Google's error classes.
        raise GeminiError(f"Gemini request failed: {e}") from e

    # response.text is the convenient shortcut for the generated text.
    # It can be None if the model returned nothing (e.g. blocked content).
    if not response.text:
        raise GeminiError("Gemini returned an empty response.")

    return response.text

"""
Embeddings — turning text into vectors of numbers that capture MEANING.

An embedding is a list of floats (here, 3072 of them) that represents a piece
of text as a point in high-dimensional space. The key property: texts with
similar MEANING land near each other, even if they use different words. That's
what lets us find "relevant" chunks by measuring distance between vectors.

We use Gemini's embedding model. Note it's a SEPARATE model from the chat model.
"""

from google.genai import types

from app.services.gemini_service import client, GeminiError

EMBED_MODEL = "gemini-embedding-001"


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts, returning one vector per text."""
    try:
        result = client.models.embed_content(model=EMBED_MODEL, contents=texts)
    except Exception as e:
        raise GeminiError(f"Embedding request failed: {e}") from e
    return [e.values for e in result.embeddings]


def embed_query(text: str) -> list[float]:
    """Embed a single query string into one vector."""
    return embed_texts([text])[0]

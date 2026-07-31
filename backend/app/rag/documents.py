"""
Document processing: PDF -> text -> chunks.

Two steps:
  1. extract_text: pull the raw text out of a PDF (using pypdf).
  2. chunk_text:   split that text into small overlapping pieces.

WHY CHUNK? Two reasons:
  - We embed and search at the chunk level. Small chunks give PRECISE matches
    (a whole 20-page document embedded as one vector is too coarse to be useful).
  - The overlap means a sentence split across a chunk boundary still appears
    (mostly) intact in at least one chunk, so we don't lose context at the seams.
"""

from io import BytesIO

from pypdf import PdfReader


def extract_text(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF given as raw bytes."""
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """
    Split text into overlapping character windows.

    chunk_size = how big each piece is; overlap = how much consecutive pieces
    share (so context isn't lost at the boundaries).
    """
    # Normalise whitespace so chunk sizes are meaningful.
    text = " ".join(text.split())
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    step = max(chunk_size - overlap, 1)
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += step
    return chunks

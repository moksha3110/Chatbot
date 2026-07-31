"""
A minimal in-memory vector store with cosine-similarity search.

A real project would use a vector DATABASE (Chroma, Pinecone, pgvector, ...).
We build a tiny one by hand so you can SEE exactly what "similarity search" is:
just measuring the angle between the query vector and each stored vector, and
returning the closest ones. No magic.

Like the conversation memory, this lives in RAM and is lost on restart — a real
vector DB (persistent) is the production upgrade, and only this file would change.
"""

import math


class VectorStore:
    def __init__(self):
        # Each item is (chunk_text, embedding_vector).
        self._items: list[tuple[str, list[float]]] = []

    def add(self, chunks: list[str], embeddings: list[list[float]]) -> None:
        for chunk, emb in zip(chunks, embeddings):
            self._items.append((chunk, emb))

    def is_empty(self) -> bool:
        return not self._items

    def count(self) -> int:
        return len(self._items)

    def search(self, query_embedding: list[float], k: int = 3) -> list[str]:
        """Return the `k` chunks whose vectors are most similar to the query."""
        scored = [
            (self._cosine(query_embedding, emb), chunk)
            for chunk, emb in self._items
        ]
        # Highest similarity first.
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [chunk for _score, chunk in scored[:k]]

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        """Cosine similarity: 1.0 = identical direction, 0 = unrelated."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# App-wide store instance (all uploaded documents share it).
vector_store = VectorStore()

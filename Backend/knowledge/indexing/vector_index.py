"""Vector index with cosine similarity and an injected embedder."""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

__all__ = ["VectorIndex", "cosine_similarity"]

EmbedFn = Callable[[str], Sequence[float]]


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity between two equal-length vectors."""
    if len(a) != len(b):
        raise ValueError("vectors must have equal length")
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class VectorIndex:
    """Flat vector store. Embeddings come from an injected embedder.

    The embedder is a callable mapping text -> vector; no ML library is
    required. Callers may inject any deterministic embedding function.
    """

    def __init__(self, embedder: Optional[EmbedFn] = None) -> None:
        self._embedder = embedder
        self._vectors: Dict[str, Sequence[float]] = {}
        self._texts: Dict[str, str] = {}

    def set_embedder(self, embedder: EmbedFn) -> None:
        """Set or replace the embedder used for future additions/queries."""
        self._embedder = embedder

    def _require_embedder(self) -> EmbedFn:
        if self._embedder is None:
            raise RuntimeError("no embedder configured; call set_embedder()")
        return self._embedder

    def add(self, doc_id: str, text: str) -> None:
        """Embed and store *text* under *doc_id*."""
        self._vectors[doc_id] = tuple(self._require_embedder()(text))
        self._texts[doc_id] = text

    def remove(self, doc_id: str) -> None:
        """Remove a document (no-op if absent)."""
        self._vectors.pop(doc_id, None)
        self._texts.pop(doc_id, None)

    def search(
        self, query: str, top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Return (doc_id, cosine similarity) sorted by descending score."""
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        qv = tuple(self._require_embedder()(query))
        scored = [
            (doc_id, cosine_similarity(qv, vec))
            for doc_id, vec in self._vectors.items()
        ]
        scored.sort(key=lambda kv: (-kv[1], kv[0]))
        return scored[:top_k]

    def text(self, doc_id: str) -> Optional[str]:
        """Stored text for *doc_id*, or None."""
        return self._texts.get(doc_id)

    def __len__(self) -> int:
        return len(self._vectors)

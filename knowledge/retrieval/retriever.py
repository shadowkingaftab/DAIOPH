"""Generic retriever over any index exposing search()."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Protocol, Tuple

__all__ = ["Retriever", "Hit", "SupportsSearch"]


class SupportsSearch(Protocol):
    """Anything with search(query, top_k) -> list of (id, score)."""

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        ...  # pragma: no cover


@dataclass(frozen=True)
class Hit:
    """A single retrieval hit."""

    doc_id: str
    score: float


class Retriever:
    """Thin wrapper adding score normalization and hit objects."""

    def __init__(self, index: SupportsSearch) -> None:
        self._index = index

    def retrieve(self, query: str, top_k: int = 5) -> List[Hit]:
        """Retrieve top_k hits for *query*."""
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        return [
            Hit(doc_id=str(doc_id), score=float(score))
            for doc_id, score in self._index.search(query, top_k=top_k)
        ]

    def retrieve_normalized(self, query: str, top_k: int = 5) -> List[Hit]:
        """Hits with scores scaled to [0, 1] by the max score (if > 0)."""
        hits = self.retrieve(query, top_k=top_k)
        peak = max((h.score for h in hits), default=0.0)
        if peak <= 0.0:
            return hits
        return [
            Hit(doc_id=h.doc_id, score=h.score / peak) for h in hits
        ]

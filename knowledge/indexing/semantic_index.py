"""Semantic index: vector index plus optional lexical fallback merge."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from knowledge.indexing.lexical_index import LexicalIndex
from knowledge.indexing.vector_index import VectorIndex

__all__ = ["SemanticIndex"]

EmbedFn = Callable[[str], "Sequence[float]"]  # noqa: F821


class SemanticIndex:
    """Combines a vector index (primary) with a lexical index (fallback).

    When the embedder yields an all-zero vector (no signal), lexical
    results are returned instead so retrieval never silently degrades.
    """

    def __init__(self, embedder: Optional[EmbedFn] = None) -> None:
        self.vector = VectorIndex(embedder)
        self.lexical = LexicalIndex()

    def set_embedder(self, embedder: EmbedFn) -> None:
        """Set the embedder on the underlying vector index."""
        self.vector.set_embedder(embedder)

    def add(self, doc_id: str, text: str) -> None:
        """Add a document to both underlying indexes."""
        self.vector.add(doc_id, text)
        self.lexical.add(doc_id, text)

    def remove(self, doc_id: str) -> None:
        """Remove a document from both underlying indexes."""
        self.vector.remove(doc_id)
        self.lexical.remove(doc_id)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Search semantically; fall back to lexical when vectors are flat."""
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        results = self.vector.search(query, top_k=top_k)
        if results and all(score == 0.0 for _, score in results):
            return self.lexical.search(query, top_k=top_k)
        return results

    def __len__(self) -> int:
        return len(self.vector)

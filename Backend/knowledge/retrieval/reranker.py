"""Reranking utilities over candidate documents."""

from __future__ import annotations

from typing import Callable, List, Sequence, Tuple

__all__ = ["rerank", "keyword_overlap_scorer"]

Doc = Tuple[str, str]  # (doc_id, text)
Scorer = Callable[[str, str], float]


def keyword_overlap_scorer(query: str, text: str) -> float:
    """Fraction of query keywords present in *text* (case-insensitive)."""
    q_words = {w for w in query.lower().split() if w}
    if not q_words:
        return 0.0
    t_words = set(text.lower().split())
    return len(q_words & t_words) / len(q_words)


def rerank(
    query: str,
    docs: Sequence[Doc],
    scorer: Scorer = keyword_overlap_scorer,
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """Score each (doc_id, text) with *scorer* and return the best top_k.

    Deterministic: ties break by doc id ascending.
    """
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    scored = [(doc_id, float(scorer(query, text))) for doc_id, text in docs]
    scored.sort(key=lambda kv: (-kv[1], kv[0]))
    return scored[:top_k]

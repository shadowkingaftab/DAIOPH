"""Hybrid search: weighted merge of lexical and vector results."""

from __future__ import annotations

from typing import Dict, List, Tuple

from knowledge.indexing.lexical_index import LexicalIndex
from knowledge.indexing.vector_index import VectorIndex

__all__ = ["hybrid_search"]


def _normalize(pairs: List[Tuple[str, float]]) -> Dict[str, float]:
    peak = max((s for _, s in pairs), default=0.0)
    if peak <= 0.0:
        return {doc_id: 0.0 for doc_id, _ in pairs}
    return {doc_id: s / peak for doc_id, s in pairs}


def hybrid_search(
    lexical: LexicalIndex,
    vector: VectorIndex,
    query: str,
    top_k: int = 5,
    lexical_weight: float = 0.5,
) -> List[Tuple[str, float]]:
    """Merge lexical and vector rankings with a weighted linear score.

    Both result lists are min-max normalized to [0, 1] by their own peak
    score, then combined as ``w * lexical + (1 - w) * vector``. Ties break
    by doc id for determinism.
    """
    if top_k < 1:
        raise ValueError("top_k must be >= 1")
    if not 0.0 <= lexical_weight <= 1.0:
        raise ValueError("lexical_weight must be within [0, 1]")
    lex = _normalize(lexical.search(query, top_k=top_k * 2))
    vec = _normalize(vector.search(query, top_k=top_k * 2))
    combined: Dict[str, float] = {}
    for doc_id in set(lex) | set(vec):
        combined[doc_id] = (
            lexical_weight * lex.get(doc_id, 0.0)
            + (1.0 - lexical_weight) * vec.get(doc_id, 0.0)
        )
    ranked = sorted(combined.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[:top_k]

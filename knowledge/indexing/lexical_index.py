"""Lexical inverted index with deterministic TF scoring."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, List, Tuple

__all__ = ["LexicalIndex", "tokenize"]

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> List[str]:
    """Lowercase word-boundary tokenization."""
    return _TOKEN_RE.findall(text.lower())


class LexicalIndex:
    """Inverted index over documents with TF-IDF-free TF scoring.

    Deterministic: scores depend only on inserted documents and the query.
    """

    def __init__(self) -> None:
        self._docs: Dict[str, str] = {}
        self._postings: Dict[str, Dict[str, int]] = {}

    def add(self, doc_id: str, text: str) -> None:
        """Index *text* under *doc_id* (re-indexing replaces the old text)."""
        if doc_id in self._docs:
            self.remove(doc_id)
        self._docs[doc_id] = text
        for token, count in Counter(tokenize(text)).items():
            self._postings.setdefault(token, {})[doc_id] = count

    def remove(self, doc_id: str) -> None:
        """Remove a document from the index (no-op if absent)."""
        text = self._docs.pop(doc_id, None)
        if text is None:
            return
        for token in tokenize(text):
            docs = self._postings.get(token)
            if docs is not None:
                docs.pop(doc_id, None)
                if not docs:
                    del self._postings[token]

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Return (doc_id, score) pairs sorted by descending TF score.

        Score is the sum over query terms of log(1 + tf). Documents
        matching more query terms and with higher term frequency rank first.
        """
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        scores: Dict[str, float] = {}
        for token in tokenize(query):
            for doc_id, tf in self._postings.get(token, {}).items():
                scores[doc_id] = scores.get(doc_id, 0.0) + math.log1p(tf)
        ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:top_k]

    def __len__(self) -> int:
        return len(self._docs)

    def doc_ids(self) -> List[str]:
        """All indexed document ids in insertion order."""
        return list(self._docs)

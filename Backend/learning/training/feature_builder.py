"""Feature building: fixed-vocabulary bag-of-words vectors."""

from __future__ import annotations

import re
from typing import Dict, List, Sequence, Tuple

__all__ = ["FeatureBuilder"]

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class FeatureBuilder:
    """Builds sparse bag-of-words features from a fixed vocabulary.

    The vocabulary is learned from ``fit`` (insertion order) and frozen
    thereafter; unseen tokens at transform time are ignored.
    """

    def __init__(self, max_features: int = 512) -> None:
        if max_features < 1:
            raise ValueError("max_features must be >= 1")
        self._max_features = max_features
        self._vocab: Dict[str, int] = {}

    @property
    def vocabulary(self) -> List[str]:
        """Feature tokens in index order."""
        return list(self._vocab)

    def fit(self, texts: Sequence[str]) -> "FeatureBuilder":
        """Learn the vocabulary from *texts* (most frequent first)."""
        counts: Dict[str, int] = {}
        for text in texts:
            for token in _TOKEN_RE.findall(text.lower()):
                counts[token] = counts.get(token, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        self._vocab = {
            token: idx
            for idx, (token, _) in enumerate(ranked[: self._max_features])
        }
        return self

    def transform(self, text: str) -> List[Tuple[int, float]]:
        """Sparse (index, count) features for *text*."""
        counts: Dict[int, float] = {}
        for token in _TOKEN_RE.findall(text.lower()):
            idx = self._vocab.get(token)
            if idx is not None:
                counts[idx] = counts.get(idx, 0.0) + 1.0
        return sorted(counts.items())

    def fit_transform(self, texts: Sequence[str]) -> List[List[Tuple[int, float]]]:
        """Fit on *texts* then transform each one."""
        self.fit(texts)
        return [self.transform(t) for t in texts]

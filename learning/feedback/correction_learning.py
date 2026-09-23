"""Learning from user corrections with normalized-input lookup."""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

__all__ = ["CorrectionLearner"]

_WS_RE = re.compile(r"\s+")


class CorrectionLearner:
    """Stores (input, wrong_output, corrected_output) triples.

    Suggestions are looked up by whitespace-normalized input so minor
    formatting differences still match. Deterministic: the most frequent
    correction wins, ties break by insertion order.
    """

    def __init__(self) -> None:
        self._corrections: Dict[str, List[Tuple[str, str]]] = {}

    @staticmethod
    def _normalize(text: str) -> str:
        return _WS_RE.sub(" ", text.strip().lower())

    def record(
        self, input_text: str, wrong_output: str, corrected_output: str
    ) -> bool:
        """Record a correction; returns False when it is a no-op."""
        if wrong_output == corrected_output:
            return False
        key = self._normalize(input_text)
        self._corrections.setdefault(key, []).append(
            (wrong_output, corrected_output)
        )
        return True

    def suggest(self, input_text: str) -> Optional[str]:
        """Most-recorded corrected output for this input, or None."""
        entries = self._corrections.get(self._normalize(input_text))
        if not entries:
            return None
        counts: Dict[str, int] = {}
        for _, corrected in entries:
            counts[corrected] = counts.get(corrected, 0) + 1
        best = max(counts.items(), key=lambda kv: (kv[1], -entries.index(
            next(e for e in entries if e[1] == kv[0])
        )))
        return best[0]

    def known_inputs(self) -> List[str]:
        """Normalized inputs with at least one correction, sorted."""
        return sorted(self._corrections)

    def __len__(self) -> int:
        return len(self._corrections)

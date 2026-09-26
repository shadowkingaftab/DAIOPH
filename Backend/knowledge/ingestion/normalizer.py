from __future__ import annotations

import re
from typing import List


class TextNormalizer:
    """Normalizes text for consistent processing."""

    def __init__(self) -> None:
        self.whitespace_re = re.compile(r"\s+")
        self.punctuation_re = re.compile(r"[^\w\s]")

    def normalize(self, text: str) -> str:
        """Normalize text by collapsing whitespace and trimming."""
        text = self.whitespace_re.sub(" ", text)
        return text.strip()

    def remove_punctuation(self, text: str) -> str:
        """Remove punctuation from text."""
        return self.punctuation_re.sub("", text)

    def to_lower(self, text: str) -> str:
        """Convert text to lowercase."""
        return text.lower()

    def normalize_tokens(self, tokens: List[str]) -> List[str]:
        """Normalize a list of tokens."""
        return [self.normalize(t) for t in tokens if self.normalize(t)]
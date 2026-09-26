from __future__ import annotations

from typing import List


class TextChunker:
    """Splits text into smaller chunks."""

    def __init__(self, chunk_size: int = 512, overlap: int = 64) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        """Split text into overlapping chunks of the configured size."""
        if not text:
            return []
        chunks: List[str] = []
        start = 0
        length = len(text)
        while start < length:
            end = min(start + self.chunk_size, length)
            chunks.append(text[start:end])
            if end == length:
                break
            start = max(end - self.overlap, start + 1)
        return chunks


class SentenceChunker(TextChunker):
    """Splits text into chunks at sentence boundaries."""

    def __init__(
        self, chunk_size: int = 512, overlap: int = 64
    ) -> None:
        super().__init__(chunk_size, overlap)

    def chunk(self, text: str) -> List[str]:
        """Split text into chunks at sentence boundaries."""
        import re

        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: List[str] = []
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) + 1 > self.chunk_size:
                if current:
                    chunks.append(current.strip())
                current = sentence
            else:
                current = current + " " + sentence if current else sentence
        if current:
            chunks.append(current.strip())
        return chunks
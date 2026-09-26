from typing import List


def chunk_text(text: str, max_tokens: int = 800, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks to stay within model context limits.

    Args:
        text: The full text to chunk.
        max_tokens: Approximate max words per chunk (proxy for tokens).
        overlap: Number of words to overlap between chunks for context continuity.

    Returns:
        A list of text chunks.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start = end - overlap  # Overlap for continuity

    return chunks


def smart_truncate(text: str, max_chars: int = 3000) -> str:
    """Truncate text to a max character count, ending at the last complete sentence."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_period = truncated.rfind(".")
    if last_period != -1:
        return truncated[: last_period + 1]
    return truncated

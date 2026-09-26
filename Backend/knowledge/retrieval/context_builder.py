"""Context builder: assemble retrieved snippets into a bounded prompt."""

from __future__ import annotations

from typing import Iterable, List, Sequence

__all__ = ["build_context", "ContextSnippet"]


class ContextSnippet:
    """A labeled snippet of text for context assembly."""

    __slots__ = ("doc_id", "text")

    def __init__(self, doc_id: str, text: str) -> None:
        self.doc_id = doc_id
        self.text = text

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"ContextSnippet(doc_id={self.doc_id!r})"


def build_context(
    snippets: Sequence[ContextSnippet], max_chars: int = 2000
) -> str:
    """Join snippets as ``[doc_id] text`` blocks within a character budget.

    Snippets are included in order until the budget is exhausted; a snippet
    that does not fit is truncated to the remaining space. At least one
    snippet is always included (possibly truncated) when any are given.
    """
    if max_chars < 1:
        raise ValueError("max_chars must be >= 1")
    blocks: List[str] = []
    used = 0
    for snip in snippets:
        header = f"[{snip.doc_id}] "
        allowance = max_chars - used - len(header)
        if allowance <= 0 and blocks:
            break
        body = snip.text[: max(allowance, 1)]
        block = header + body
        blocks.append(block)
        used += len(block) + 1  # +1 for the joining newline
        if used >= max_chars:
            break
    return "\n".join(blocks)

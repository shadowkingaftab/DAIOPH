"""Document summarizer (word/char counts; no external deps)."""

from __future__ import annotations

from typing import Dict, Any

from tools.registry.tool_schema import ToolSchema

__all__ = ["summarize_document", "doc_summarize"]


def summarize_document(text: str) -> Dict[str, Any]:
    """Return word/char counts and a first-sentence preview."""
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "preview": " ".join(words[:20]),
    }


doc_summarize = ToolSchema(
    name="doc_summarize",
    description="Summarize a document: word/char counts and preview",
    fn=summarize_document,
    params={"text": str},
)

"""Minimal HTML text extractor (stdlib html.parser)."""


from __future__ import annotations

from html.parser import HTMLParser
from typing import List

from tools.registry.tool_schema import ToolSchema

__all__ = ["extract_html_text", "web_extract"]


class _TextExtractor(HTMLParser):
    """Collects text nodes while skipping script/style tags."""

    def __init__(self) -> None:
        super().__init__()
        self._skip = 0
        self.parts: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self.parts.append(data.strip())


def extract_html_text(html: str, max_chars: int = 0) -> str:
    """Extract visible text from *html*, skipping script/style content."""
    parser = _TextExtractor()
    parser.feed(html)
    joined = " ".join(parser.parts)
    return joined[:max_chars] if max_chars > 0 else joined


web_extract = ToolSchema(
    name="web_extract",
    description="Extract visible text from an HTML document",
    fn=extract_html_text,
    params={"html": str, "max_chars": int},
)

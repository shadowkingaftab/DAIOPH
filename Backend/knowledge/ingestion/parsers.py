from __future__ import annotations

from typing import Any, List


class DocumentParser:
    """Base class for document parsers."""

    def parse(self, raw: Any) -> str:
        """Parse raw content into plain text."""
        raise NotImplementedError


class TextParser(DocumentParser):
    """Parses plain text content."""

    def parse(self, raw: Any) -> str:
        """Return the raw content as-is if it is a string."""
        return str(raw)


class JsonParser(DocumentParser):
    """Parses JSON content into a text representation."""

    def parse(self, raw: Any) -> str:
        """Convert a JSON object into a readable text form."""
        import json

        if isinstance(raw, str):
            data = json.loads(raw)
        else:
            data = raw
        return json.dumps(data, indent=2, ensure_ascii=False)


class CsvParser(DocumentParser):
    """Parses CSV content into a text representation."""

    def parse(self, raw: Any) -> str:
        """Convert CSV rows into a readable text form."""
        if isinstance(raw, str):
            return raw
        lines: List[str] = []
        for row in raw:
            lines.append(", ".join(str(v) for v in row.values()))
        return "\n".join(lines)
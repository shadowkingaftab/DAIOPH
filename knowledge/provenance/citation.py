"""Citations linking statements back to sources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from knowledge.provenance.source import Source

__all__ = ["Citation", "CitationRegistry"]


@dataclass(frozen=True)
class Citation:
    """A statement attributed to one source."""

    statement: str
    source_id: str


class CitationRegistry:
    """Registry of sources and citations with formatted output."""

    def __init__(self) -> None:
        self._sources: Dict[str, Source] = {}
        self._citations: List[Citation] = []

    def register_source(self, source: Source) -> Source:
        """Register a source (duplicate ids raise ValueError)."""
        if source.source_id in self._sources:
            raise ValueError(f"duplicate source id: {source.source_id!r}")
        self._sources[source.source_id] = source
        return source

    def cite(self, statement: str, source_id: str) -> Citation:
        """Record a citation; the source must already be registered."""
        if source_id not in self._sources:
            raise KeyError(f"unknown source: {source_id!r}")
        citation = Citation(statement=statement, source_id=source_id)
        self._citations.append(citation)
        return citation

    def format(self, citation: Citation) -> str:
        """Human-readable citation string."""
        source = self._sources[citation.source_id]
        return f'"{citation.statement}" [{source.source_id}: {source.uri}]'

    def citations_for(self, source_id: str) -> List[Citation]:
        """All citations attributed to *source_id*."""
        return [c for c in self._citations if c.source_id == source_id]

    def source(self, source_id: str) -> Optional[Source]:
        """Fetch a registered source, or None."""
        return self._sources.get(source_id)

    def __len__(self) -> int:
        return len(self._citations)

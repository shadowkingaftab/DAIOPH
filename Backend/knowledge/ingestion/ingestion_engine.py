from __future__ import annotations

from typing import Any, Dict, List


class IngestionEngine:
    """Orchestrates the ingestion of documents into the knowledge base."""

    def __init__(self) -> None:
        self.loaders: Dict[str, Any] = {}
        self.parsers: Dict[str, Any] = {}
        self.chunker: Any = None
        self.normalizer: Any = None
        self.ingested_documents: List[str] = []

    def register_loader(self, name: str, loader: Any) -> None:
        """Register a document loader by name."""
        self.loaders[name] = loader

    def register_parser(self, name: str, parser: Any) -> None:
        """Register a document parser by name."""
        self.parsers[name] = parser

    def set_chunker(self, chunker: Any) -> None:
        """Set the chunker to use for splitting documents."""
        self.chunker = chunker

    def set_normalizer(self, normalizer: Any) -> None:
        """Set the normalizer to use for cleaning text."""
        self.normalizer = normalizer

    def ingest(
        self, source: str, loader_name: str = "default"
    ) -> Dict[str, Any]:
        """Ingest a document from a source.

        Returns:
            A dictionary describing the ingestion result.
        """
        loader = self.loaders.get(loader_name)
        if loader is None:
            raise ValueError(
                f"No loader registered under '{loader_name}'"
            )
        raw = loader.load(source)
        parser = self.parsers.get(loader_name)
        text = parser.parse(raw) if parser is not None else str(raw)
        chunks = (
            self.chunker.chunk(text)
            if self.chunker is not None
            else [text]
        )
        normalized = (
            [self.normalizer.normalize(c) for c in chunks]
            if self.normalizer is not None
            else chunks
        )
        self.ingested_documents.append(source)
        return {
            "source": source,
            "chunks": normalized,
            "count": len(normalized),
        }

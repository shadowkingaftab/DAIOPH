from __future__ import annotations

from typing import Any, Dict, List


class DocumentLoader:
    """Base class for document loaders."""

    def __init__(self) -> None:
        self.supported_extensions: List[str] = []

    def load(self, source: str) -> Any:
        """Load a document from a source path."""
        raise NotImplementedError

    def supports(self, source: str) -> bool:
        """Check if this loader supports the given source."""
        ext = source.rsplit(".", 1)[-1].lower() if "." in source else ""
        return ext in self.supported_extensions


class TextLoader(DocumentLoader):
    """Loads plain text files."""

    def __init__(self) -> None:
        super().__init__()
        self.supported_extensions = ["txt", "md", "rst"]

    def load(self, source: str) -> str:
        """Read and return the contents of a text file."""
        with open(source, "r", encoding="utf-8") as f:
            return f.read()


class JsonLoader(DocumentLoader):
    """Loads JSON files."""

    def __init__(self) -> None:
        super().__init__()
        self.supported_extensions = ["json"]

    def load(self, source: str) -> Dict[str, Any]:
        """Read and return the contents of a JSON file."""
        import json

        with open(source, "r", encoding="utf-8") as f:
            return json.load(f)


class CsvLoader(DocumentLoader):
    """Loads CSV files."""

    def __init__(self) -> None:
        super().__init__()
        self.supported_extensions = ["csv"]

    def load(self, source: str) -> List[Dict[str, Any]]:
        """Read and return the contents of a CSV file."""
        import csv

        rows: List[Dict[str, Any]] = []
        with open(source, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
        return rows
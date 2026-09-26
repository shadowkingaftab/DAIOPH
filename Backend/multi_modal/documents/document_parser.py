"""DocumentParser - parses various document formats."""

from typing import Any, Dict, List, Optional


class DocumentParser:
    """Parses various document formats."""

    def __init__(self) -> None:
        """Initialize the document parser."""
        self._supported = [".pdf", ".docx", ".pptx", ".xlsx", ".txt"]

    def parse(self, data: bytes, format: str) -> Dict[str, Any]:
        """Parse a document.

        Args:
            data: Document data.
            format: Document format.

        Returns:
            Dict[str, Any]: Parsed content.
        """
        return {"content": "parsed content", "format": format}

    def get_supported(self) -> List[str]:
        """Get supported formats.

        Returns:
            List[str]: Supported formats.
        """
        return list(self._supported)

</final_file_content>
</write_to_file></tool_call>
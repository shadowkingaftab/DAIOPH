"""DocumentProcessor - processes document input."""

from typing import Any, Dict, List, Optional


class DocumentProcessor:
    """Processes document input for multimodal pipeline."""

    def __init__(self) -> None:
        """Initialize the document processor."""
        self._supported_formats = [".pdf", ".docx", ".txt", ".pptx", ".xlsx"]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process document input.

        Args:
            input_data: Input data dict.

        Returns:
            Dict[str, Any]: Processed result.
        """
        document = input_data.get("document", None)
        return {"document": document, "formats": self._supported_formats, "processed": True}

    def get_supported_formats(self) -> List[str]:
        """Get supported formats.

        Returns:
            List[str]: Supported formats.
        """
        return list(self._supported_formats)

</final_file_content>
</write_to_file></tool_call>
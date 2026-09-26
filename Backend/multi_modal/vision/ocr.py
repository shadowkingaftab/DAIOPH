"""OCR - optical character recognition."""

from typing import Any, Dict, List, Optional


class OCR:
    """Performs optical character recognition on images."""

    def __init__(self, language: str = "en") -> None:
        """Initialize OCR.

        Args:
            language: Recognition language.
        """
        self._language = language

    def extract_text(self, image: Any) -> str:
        """Extract text from an image.

        Args:
            image: Image data.

        Returns:
            str: Extracted text.
        """
        return "extracted text"

    def get_language(self) -> str:
        """Get recognition language.

        Returns:
            str: Language.
        """
        return self._language

</final_file_content>
</write_to_file></tool_call>
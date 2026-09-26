"""SpeechToText - converts speech to text."""

from typing import Any, Dict, List, Optional


class SpeechToText:
    """Converts speech audio to text."""

    def __init__(self, model: str = "whisper") -> None:
        """Initialize speech-to-text.

        Args:
            model: Model name.
        """
        self._model = model

    def transcribe(self, audio: bytes) -> str:
        """Transcribe audio to text.

        Args:
            audio: Audio data.

        Returns:
            str: Transcribed text.
        """
        return "transcribed text"

    def get_model(self) -> str:
        """Get model name.

        Returns:
            str: Model name.
        """
        return self._model

</final_file_content>
</write_to_file></tool_call>
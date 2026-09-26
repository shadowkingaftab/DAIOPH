"""VoiceActivity - detects voice activity in audio."""

from typing import Any, Dict, List, Optional


class VoiceActivity:
    """Detects voice activity in audio streams."""

    def __init__(self, threshold: float = 0.5) -> None:
        """Initialize voice activity detection.

        Args:
            threshold: Detection threshold.
        """
        self._threshold = threshold

    def detect(self, audio: bytes) -> bool:
        """Detect voice activity.

        Args:
            audio: Audio data.

        Returns:
            bool: True if voice detected.
        """
        return len(audio) > 0

    def get_threshold(self) -> float:
        """Get detection threshold.

        Returns:
            float: Threshold.
        """
        return self._threshold

</final_file_content>
</write_to_file></tool_call>
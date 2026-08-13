"""TemporalContext - manages temporal context for video."""

from typing import Any, Dict, List, Optional


class TemporalContext:
    """Manages temporal context for video processing."""

    def __init__(self) -> None:
        """Initialize temporal context."""
        self._frames: List[Dict[str, Any]] = []
        self._timestamps: List[float] = []

    def add_frame(self, frame: Dict[str, Any], timestamp: float) -> None:
        """Add a frame with timestamp.

        Args:
            frame: Frame data.
            timestamp: Frame timestamp.
        """
        self._frames.append(frame)
        self._timestamps.append(timestamp)

    def get_context(self, window: float = 5.0) -> List[Dict[str, Any]]:
        """Get temporal context window.

        Args:
            window: Time window in seconds.

        Returns:
            List[Dict[str, Any]]: Context frames.
        """
        return list(self._frames)

    def clear(self) -> None:
        """Clear all context."""
        self._frames = []
        self._timestamps = []

</final_file_content>
</write_to_file></tool_call>
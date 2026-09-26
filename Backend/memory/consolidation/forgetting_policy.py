"""ForgettingPolicy - manages memory forgetting."""

from typing import Any, Dict, List, Optional


class ForgettingPolicy:
    """Manages memory forgetting based on age and importance."""

    def __init__(self, max_age: int = 86400) -> None:
        """Initialize the forgetting policy.

        Args:
            max_age: Maximum age in seconds.
        """
        self._max_age = max_age
        self._timestamps: Dict[str, float] = {}

    def mark(self, key: str, timestamp: float) -> None:
        """Mark a memory with a timestamp.

        Args:
            key: Memory key.
            timestamp: Creation timestamp.
        """
        self._timestamps[key] = timestamp

    def should_forget(self, key: str, current_time: float, importance: float = 0.5) -> bool:
        """Check if a memory should be forgotten.

        Args:
            key: Memory key.
            current_time: Current timestamp.
            importance: Importance score (0-1).

        Returns:
            bool: True if should forget.
        """
        age = current_time - self._timestamps.get(key, current_time)
        return age > self._max_age and importance < 0.3

    def get_expired(self, current_time: float) -> List[str]:
        """Get expired memory keys.

        Args:
            current_time: Current timestamp.

        Returns:
            List[str]: Expired keys.
        """
        return [k for k, t in self._timestamps.items() if current_time - t > self._max_age]

</final_file_content>
</write_to_file></tool_call>
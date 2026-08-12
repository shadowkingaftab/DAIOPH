"""Importance - calculates memory importance scores."""

from typing import Any, Dict, Optional


class Importance:
    """Calculates importance scores for memories."""

    def __init__(self) -> None:
        """Initialize the importance calculator."""
        self._scores: Dict[str, float] = {}

    def score(self, key: str, value: float) -> None:
        """Set an importance score.

        Args:
            key: Memory key.
            value: Importance score (0-1).
        """
        self._scores[key] = value

    def get(self, key: str, default: float = 0.5) -> float:
        """Get an importance score.

        Args:
            key: Memory key.
            default: Default score.

        Returns:
            float: Importance score.
        """
        return self._scores.get(key, default)

    def rank(self) -> List[str]:
        """Rank memories by importance.

        Returns:
            List[str]: Keys sorted by importance.
        """
        return sorted(self._scores.keys(), key=lambda k: self._scores[k], reverse=True)

</final_file_content>
</write_to_file></tool_call>
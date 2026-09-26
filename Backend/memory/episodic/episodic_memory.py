"""EpisodicMemory - stores and retrieves episodic memories."""

from typing import Any, Dict, List, Optional


class EpisodicMemory:
    """Stores and retrieves episodic memory traces."""

    def __init__(self, capacity: int = 1000) -> None:
        """Initialize episodic memory.

        Args:
            capacity: Maximum number of episodes.
        """
        self._capacity = capacity
        self._episodes: List[Dict[str, Any]] = []

    def store(self, episode: Dict[str, Any]) -> None:
        """Store an episode.

        Args:
            episode: Episode data.
        """
        if len(self._episodes) >= self._capacity:
            self._episodes.pop(0)
        self._episodes.append(episode)

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve episodes matching a query.

        Args:
            query: Search query.

        Returns:
            List[Dict[str, Any]]: Matching episodes.
        """
        return [e for e in self._episodes if query.lower() in str(e).lower()]

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all episodes.

        Returns:
            List[Dict[str, Any]]: All episodes.
        """
        return list(self._episodes)

    def clear(self) -> None:
        """Clear all episodes."""
        self._episodes = []

</final_file_content>
</write_to_file></tool_call>
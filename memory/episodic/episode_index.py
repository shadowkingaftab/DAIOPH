"""EpisodeIndex - indexes episodes for fast retrieval."""

from typing import Any, Dict, List, Optional


class EpisodeIndex:
    """Indexes episodes for fast retrieval."""

    def __init__(self) -> None:
        """Initialize the episode index."""
        self._index: Dict[str, List[str]] = {}

    def index(self, episode_id: str, tags: List[str]) -> None:
        """Index an episode by tags.

        Args:
            episode_id: Episode identifier.
            tags: Tags to index by.
        """
        for tag in tags:
            if tag not in self._index:
                self._index[tag] = []
            self._index[tag].append(episode_id)

    def lookup(self, tag: str) -> List[str]:
        """Look up episodes by tag.

        Args:
            tag: Tag to look up.

        Returns:
            List[str]: Episode IDs.
        """
        return self._index.get(tag, [])

    def get_all_tags(self) -> List[str]:
        """Get all indexed tags.

        Returns:
            List[str]: All tags.
        """
        return list(self._index.keys())

</final_file_content>
</write_to_file></tool_call>
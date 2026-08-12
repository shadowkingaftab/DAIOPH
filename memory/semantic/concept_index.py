"""ConceptIndex - indexes concepts for semantic memory."""

from typing import Any, Dict, List, Optional


class ConceptIndex:
    """Indexes concepts for fast semantic lookup."""

    def __init__(self) -> None:
        """Initialize the concept index."""
        self._index: Dict[str, List[str]] = {}

    def add(self, concept: str, related: List[str]) -> None:
        """Add a concept with related concepts.

        Args:
            concept: Concept name.
            related: Related concept names.
        """
        if concept not in self._index:
            self._index[concept] = []
        self._index[concept].extend(related)

    def lookup(self, concept: str) -> List[str]:
        """Look up related concepts.

        Args:
            concept: Concept name.

        Returns:
            List[str]: Related concepts.
        """
        return self._index.get(concept, [])

    def get_all(self) -> List[str]:
        """Get all indexed concepts.

        Returns:
            List[str]: All concepts.
        """
        return list(self._index.keys())

</final_file_content>
</write_to_file></tool_call>
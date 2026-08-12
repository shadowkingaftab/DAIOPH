"""Attention - focuses cognitive resources on relevant information."""

from typing import Any, Dict, List, Optional


class Attention:
    """Manages attention allocation to relevant stimuli."""

    def __init__(self, focus_width: int = 5) -> None:
        """Initialize the attention module.

        Args:
            focus_width: Number of top items to attend to.
        """
        self._focus_width = focus_width
        self._attention_history: List[Dict[str, Any]] = []

    def attend(self, items: List[Any], context: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Select the most relevant items from a list.

        Args:
            items: List of items to attend to.
            context: Optional context for relevance scoring.

        Returns:
            List[Any]: Top-relevance items.
        """
        if not items:
            return []

        # Simple relevance scoring based on context
        if context and "priorities" in context:
            priorities = context["priorities"]
            scored = []
            for i, item in enumerate(items):
                priority = priorities.get(str(i), 0.5)
                scored.append((priority, item))
            scored.sort(reverse=True)
            return [item for _, item in scored[:self._focus_width]]

        # Default: return first N items
        return items[: self._focus_width]

    def update_focus_width(self, width: int) -> None:
        """Update the focus width.

        Args:
            width: New focus width.
        """
        self._focus_width = max(1, width)

    def get_focus_width(self) -> int:
        """Get current focus width.

        Returns:
            int: Current focus width.
        """
        return self._focus_width

    def reset(self) -> None:
        """Reset the attention module."""
        self._attention_history = []
</final_file_content>
</write_to_file>
"""VisualContext - manages visual context."""

from typing import Any, Dict, List, Optional


class VisualContext:
    """Manages visual context for multimodal processing."""

    def __init__(self) -> None:
        """Initialize visual context."""
        self._context: Dict[str, Any] = {}

    def update(self, key: str, value: Any) -> None:
        """Update context.

        Args:
            key: Context key.
            value: Context value.
        """
        self._context[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get context value.

        Args:
            key: Context key.
            default: Default if not found.

        Returns:
            Any: Context value.
        """
        return self._context.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all context.

        Returns:
            Dict[str, Any]: All context.
        """
        return dict(self._context)

</final_file_content>
</write_to_file></tool_call>
"""WorkingContext - manages active working context."""

from typing import Any, Dict, Optional


class WorkingContext:
    """Manages the active working context for short-term tasks."""

    def __init__(self) -> None:
        """Initialize working context."""
        self._context: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Set a context value.

        Args:
            key: Context key.
            value: Value to set.
        """
        self._context[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value.

        Args:
            key: Context key.
            default: Default if not found.

        Returns:
            Any: Context value.
        """
        return self._context.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all context values.

        Returns:
            Dict[str, Any]: All context.
        """
        return dict(self._context)

    def clear(self) -> None:
        """Clear the working context."""
        self._context = {}

</final_file_content>
</write_to_file></tool_call>
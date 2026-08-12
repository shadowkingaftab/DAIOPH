"""Liquid context - manages contextual information for liquid intelligence."""

import time
from typing import Any, Dict, List, Optional


class LiquidContext:
    """Stores and manages contextual information.

    Context evolves during processing and provides the situational
    awareness needed for adaptive behavior.
    """

    def __init__(self, limit: int = 100) -> None:
        """Initialize the liquid context.

        Args:
            limit: Maximum number of context entries.
        """
        self._context: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []
        self._limit = limit

    def update(self, data: Dict[str, Any]) -> None:
        """Update the context with new data.

        Args:
            data: Context data to merge.
        """
        self._context.update(data)
        self._history.append({"timestamp": time.time(), "data": dict(data)})
        if len(self._history) > self._limit:
            self._history = self._history[-self._limit:]

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value.

        Args:
            key: Context key.
            default: Default if not found.

        Returns:
            Any: Context value or default.
        """
        return self._context.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a context value.

        Args:
            key: Context key.
            value: Context value.
        """
        self._context[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Get all context values.

        Returns:
            Dict[str, Any]: Full context dict.
        """
        return dict(self._context)

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get context update history.

        Args:
            limit: Optional number of recent entries.

        Returns:
            List[Dict[str, Any]]: Context history.
        """
        if limit:
            return self._history[-limit:]
        return list(self._history)

    def reset(self) -> None:
        """Reset the context."""
        self._context = {}
        self._history = []
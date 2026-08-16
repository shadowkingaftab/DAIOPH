from __future__ import annotations

from typing import Any, Dict


class DesktopContext:
    """Provides context about the desktop environment."""

    def __init__(self) -> None:
        self.context: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Set a context value."""
        self.context[key] = value

    def get(self, key: str) -> Any:
        """Get a context value."""
        return self.context.get(key)

    def get_all(self) -> Dict[str, Any]:
        """Return all context values."""
        return dict(self.context)
from __future__ import annotations

from typing import Any, Dict, List


class WindowManager:
    """Manages desktop windows."""

    def __init__(self) -> None:
        self.windows: Dict[str, Dict[str, Any]] = {}
        self.focused: str = ""

    def create_window(self, window_id: str, title: str = "") -> bool:
        """Create a new window."""
        if window_id in self.windows:
            return False
        self.windows[window_id] = {"title": title, "visible": True}
        self.focused = window_id
        return True

    def close_window(self, window_id: str) -> bool:
        """Close and remove a window."""
        if window_id not in self.windows:
            return False
        del self.windows[window_id]
        if self.focused == window_id:
            self.focused = ""
        return True

    def focus(self, window_id: str) -> bool:
        """Focus a window."""
        if window_id not in self.windows:
            return False
        self.focused = window_id
        return True

    def get_focused(self) -> str:
        """Return the focused window ID."""
        return self.focused

    def get_windows(self) -> List[str]:
        """Return all window IDs."""
        return list(self.windows.keys())

    def get_status(self) -> Dict[str, Any]:
        """Return the window manager status."""
        return {
            "window_count": len(self.windows),
            "focused": self.focused,
            "windows": list(self.windows.keys()),
        }
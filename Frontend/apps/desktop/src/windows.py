"""Window management for the DAIOPH desktop application."""

from typing import Optional


class MainWindow:
    """Main application window controller.

    Provides a minimal window abstraction. Platform-specific renderers
    (Tkinter, Qt, Electron bridge, etc.) can be plugged in here.
    """

    def __init__(self, title: str = "DAIOPH Edge AI") -> None:
        """Initialize the main window.

        Args:
            title: Window title.
        """
        self._title = title
        self._width = 1200
        self._height = 800
        self._visible = False

    def show(self) -> None:
        """Display the window."""
        self._visible = True
        print(f"[DAIOPH Window] Showing '{self._title}' ({self._width}x{self._height})")

    def hide(self) -> None:
        """Hide the window."""
        self._visible = False

    def close(self) -> None:
        """Close the window."""
        self._visible = False
        print("[DAIOPH Window] Closed.")

    def set_title(self, title: str) -> None:
        """Set the window title.

        Args:
            title: New window title.
        """
        self._title = title

    @property
    def is_visible(self) -> bool:
        """Whether the window is currently visible."""
        return self._visible
"""System tray integration for the DAIOPH desktop application."""

from typing import Callable, Optional


class SystemTray:
    """Cross-platform system tray icon controller.

    Provides a minimal tray interface. Platform-specific backends
    (pystray, Qt, etc.) can be plugged in here.
    """

    def __init__(self, on_quit: Optional[Callable[[], None]] = None) -> None:
        """Initialize the system tray.

        Args:
            on_quit: Callback invoked when the user quits from the tray.
        """
        self._on_quit = on_quit
        self._icon = None
        self._visible = False

    def show(self) -> None:
        """Show the tray icon."""
        self._visible = True
        print("[DAIOPH Tray] Tray icon shown.")

    def hide(self) -> None:
        """Hide the tray icon."""
        self._visible = False
        print("[DAIOPH Tray] Tray icon hidden.")

    def notify(self, title: str, message: str) -> None:
        """Show a desktop notification.

        Args:
            title: Notification title.
            message: Notification body.
        """
        print(f"[DAIOPH Tray] Notification: {title} - {message}")

    def quit(self) -> None:
        """Trigger the quit callback."""
        if self._on_quit:
            self._on_quit()
"""DAIOPH Desktop Application Core.

Manages the application lifecycle, tray icon, and window management
for the DAIOPH edge AI desktop client.
"""

import sys
import threading
from typing import Optional

from apps.desktop.src.tray import SystemTray
from apps.desktop.src.windows import MainWindow
from apps.desktop.src.updater import AppUpdater


class DAIOPHApplication:
    """Main application controller for the DAIOPH desktop client."""

    def __init__(self) -> None:
        """Initialize the application."""
        self._running = False
        self._tray: Optional[SystemTray] = None
        self._window: Optional[MainWindow] = None
        self._updater = AppUpdater()
        self._backend_thread: Optional[threading.Thread] = None

    def run(self) -> int:
        """Run the application main loop.

        Returns:
            int: Exit code (0 for success).
        """
        self._running = True
        print("[DAIOPH Desktop] Starting application...")

        # Start the backend engine in a background thread
        self._backend_thread = threading.Thread(
            target=self._start_backend, daemon=True, name="daiph-backend"
        )
        self._backend_thread.start()

        # Initialize UI components
        self._window = MainWindow()
        self._tray = SystemTray(on_quit=self.shutdown)

        print("[DAIOPH Desktop] Application running. Press Ctrl+C to quit.")
        try:
            while self._running:
                # Main event loop (platform-specific implementations hook here)
                import time

                time.sleep(0.5)
        except KeyboardInterrupt:
            print("[DAIOPH Desktop] Shutting down...")
        finally:
            self.shutdown()

        return 0

    def _start_backend(self) -> None:
        """Start the DAIOPH backend engine (orchestrator, memory, etc.)."""
        try:
            from liquid_core.liquid_engine import LiquidEngine

            engine = LiquidEngine()
            print(f"[DAIOPH Desktop] Backend ready. Hardware: {engine.get_hardware_specs()}")
        except Exception as e:  # pragma: no cover - graceful degradation
            print(f"[DAIOPH Desktop] Backend failed to start: {e}")

    def shutdown(self) -> None:
        """Gracefully shut down the application."""
        if not self._running:
            return
        self._running = False
        print("[DAIOPH Desktop] Shutdown complete.")
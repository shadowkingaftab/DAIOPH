"""Shutdown manager - coordinates graceful system shutdown."""

import time
from typing import Any, Callable, Dict, List, Optional


class ShutdownManager:
    """Manages graceful shutdown of all system components.

    ShutdownManager runs cleanup hooks in reverse registration order
    and tracks shutdown progress.
    """

    def __init__(self) -> None:
        """Initialize the shutdown manager."""
        self._hooks: List[Dict[str, Any]] = []
        self._shutdown_started = False
        self._shutdown_complete = False

    def register_hook(self, name: str, fn: Callable[[], None], timeout: float = 5.0) -> None:
        """Register a shutdown hook.

        Args:
            name: Hook name.
            fn: Callable to run during shutdown.
            timeout: Maximum time to wait for the hook.
        """
        self._hooks.append({"name": name, "fn": fn, "timeout": timeout, "status": "pending"})

    def shutdown(self) -> bool:
        """Run all shutdown hooks in reverse order.

        Returns:
            bool: True if all hooks completed successfully.
        """
        if self._shutdown_started:
            return self._shutdown_complete

        self._shutdown_started = True
        success = True

        # Run hooks in reverse registration order
        for hook in reversed(self._hooks):
            try:
                hook["fn"]()
                hook["status"] = "success"
                print(f"[Shutdown] ✓ {hook['name']}")
            except Exception as e:  # pragma: no cover
                hook["status"] = "failed"
                hook["error"] = str(e)
                print(f"[Shutdown] ✗ {hook['name']}: {e}")
                success = False

        self._shutdown_complete = True
        return success

    def get_status(self) -> Dict[str, Any]:
        """Get shutdown status report.

        Returns:
            Dict[str, Any]: Shutdown status.
        """
        return {
            "started": self._shutdown_started,
            "complete": self._shutdown_complete,
            "hooks": self._hooks,
            "success": all(h["status"] == "success" for h in self._hooks),
        }
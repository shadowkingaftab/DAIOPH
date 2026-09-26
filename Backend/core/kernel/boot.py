"""Boot manager - handles system startup sequence and health checks."""

import time
from typing import Any, Callable, Dict, List, Optional


class BootManager:
    """Manages the system boot sequence.

    BootManager runs initialization steps in order and tracks
    their status for health reporting.
    """

    def __init__(self) -> None:
        """Initialize the boot manager."""
        self._steps: List[Dict[str, Any]] = []
        self._completed: List[str] = []
        self._start_time: Optional[float] = None

    def register_step(self, name: str, fn: Callable[[], None], required: bool = True) -> None:
        """Register a boot step.

        Args:
            name: Step name.
            fn: Callable to run.
            required: Whether the step is required for boot success.
        """
        self._steps.append({"name": name, "fn": fn, "required": required, "status": "pending"})

    def boot(self) -> bool:
        """Run all boot steps.

        Returns:
            bool: True if all required steps succeeded.
        """
        self._start_time = time.time()
        success = True

        for step in self._steps:
            try:
                step["fn"]()
                step["status"] = "success"
                self._completed.append(step["name"])
                print(f"[Boot] ✓ {step['name']}")
            except Exception as e:  # pragma: no cover
                step["status"] = "failed"
                step["error"] = str(e)
                print(f"[Boot] ✗ {step['name']}: {e}")
                if step["required"]:
                    success = False

        return success

    def get_status(self) -> Dict[str, Any]:
        """Get boot status report.

        Returns:
            Dict[str, Any]: Boot status.
        """
        elapsed = (time.time() - self._start_time) if self._start_time else 0
        return {
            "steps": self._steps,
            "completed": self._completed,
            "elapsed": elapsed,
            "success": all(s["status"] == "success" for s in self._steps if s["required"]),
        }
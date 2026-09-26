from __future__ import annotations

from typing import Any, Dict


class ApplicationManager:
    """Manages desktop applications."""

    def __init__(self) -> None:
        self.applications: Dict[str, Dict[str, Any]] = {}
        self.running: Dict[str, bool] = {}

    def register(self, app_id: str, info: Dict[str, Any]) -> None:
        """Register an application."""
        self.applications[app_id] = info
        self.running[app_id] = False

    def launch(self, app_id: str) -> bool:
        """Launch an application."""
        if app_id not in self.applications:
            return False
        self.running[app_id] = True
        return True

    def terminate(self, app_id: str) -> bool:
        """Terminate an application."""
        if app_id not in self.applications:
            return False
        self.running[app_id] = False
        return True

    def is_running(self, app_id: str) -> bool:
        """Check if an application is running."""
        return self.running.get(app_id, False)

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Return all registered applications."""
        return dict(self.applications)
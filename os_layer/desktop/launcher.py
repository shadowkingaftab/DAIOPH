from __future__ import annotations

from typing import Any, Dict


class Launcher:
    """Launches applications and manages the desktop environment."""

    def __init__(self) -> None:
        self.launched_apps: Dict[str, Any] = {}

    def launch(self, app_id: str, command: str) -> bool:
        """Launch an application by ID."""
        self.launched_apps[app_id] = {"command": command, "running": True}
        return True

    def terminate(self, app_id: str) -> bool:
        """Terminate a running application."""
        if app_id not in self.launched_apps:
            return False
        self.launched_apps[app_id]["running"] = False
        return True

    def is_running(self, app_id: str) -> bool:
        """Check if an application is running."""
        app = self.launched_apps.get(app_id)
        return bool(app and app.get("running", False))

    def get_running_apps(self) -> list[str]:
        """Return IDs of running applications."""
        return [
            app_id
            for app_id, app in self.launched_apps.items()
            if app.get("running", False)
        ]

    def get_status(self) -> Dict[str, Any]:
        """Return the launcher status."""
        return {
            "launched": list(self.launched_apps.keys()),
            "running": self.get_running_apps(),
        }
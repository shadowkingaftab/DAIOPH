from __future__ import annotations

from typing import Any, Dict, List


class DeviceRoute:
    """Device-related REST routes."""

    def get_status(self) -> Dict[str, Any]:
        """Get device status."""
        return {"online": True, "battery": 100}

    def get_capabilities(self) -> List[Dict[str, Any]]:
        """Get device capabilities."""
        return []

    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update device settings."""
        return {"status": "updated"}
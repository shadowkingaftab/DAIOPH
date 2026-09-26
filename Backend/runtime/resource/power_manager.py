"""Power state reporting with honest degradation.

Battery data requires platform APIs; when unavailable the manager reports
``UNKNOWN`` power source rather than assuming AC power.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional

__all__ = ["PowerMode", "PowerStatus", "PowerManager"]


class PowerMode(str, Enum):
    """Configurable performance posture."""

    PERFORMANCE = "performance"
    BALANCED = "balanced"
    SAVER = "saver"


@dataclass(frozen=True)
class PowerStatus:
    """Measured power state; ``None`` fields mean undetectable here."""

    plugged_in: Optional[bool]
    battery_percent: Optional[float]
    source: str


class PowerManager:
    """Reports power state via an injectable provider (psutil by default)."""

    def __init__(
        self,
        provider: Optional[Callable[[], PowerStatus]] = None,
        mode: PowerMode = PowerMode.BALANCED,
    ) -> None:
        self.mode = mode
        self._provider = provider or self._psutil_provider

    @staticmethod
    def _psutil_provider() -> PowerStatus:
        """Default provider using psutil's battery API when present."""
        try:
            import psutil  # type: ignore[import-not-found]

            battery = psutil.sensors_battery()  # type: ignore[attr-defined]
        except (ImportError, AttributeError, OSError):
            return PowerStatus(None, None, "unavailable")
        if battery is None:
            return PowerStatus(None, None, "no-battery-device")
        return PowerStatus(
            plugged_in=bool(battery.power_plugged),
            battery_percent=round(float(battery.percent), 1),
            source="psutil",
        )

    def status(self) -> PowerStatus:
        """Current power status (honest unknown when undetectable)."""
        return self._provider()

    def recommend_mode(self) -> PowerMode:
        """Suggest a mode from measured state; balanced when unknown."""
        status = self.status()
        if status.battery_percent is None:
            return PowerMode.BALANCED
        if not status.plugged_in and status.battery_percent < 20:
            return PowerMode.SAVER
        if status.plugged_in:
            return PowerMode.PERFORMANCE
        return PowerMode.BALANCED

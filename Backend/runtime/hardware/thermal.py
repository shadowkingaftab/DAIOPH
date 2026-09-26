"""Thermal state reporting with explicit unknown handling.

There is no portable stdlib thermal API. This module tries psutil's sensor
API when installed and otherwise reports ``UNKNOWN`` with the reason — it
never invents a temperature.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

__all__ = ["ThermalState", "ThermalReading", "read_thermal"]


class ThermalState(str, Enum):
    """Qualitative thermal condition."""

    UNKNOWN = "unknown"
    NOMINAL = "nominal"
    WARM = "warm"
    HOT = "hot"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ThermalReading:
    """One thermal measurement (or an honest unknown)."""

    state: ThermalState
    celsius: Optional[float]
    source: str
    detail: str = ""


def _classify(celsius: float) -> ThermalState:
    """Map a temperature to a qualitative state."""
    if celsius >= 90:
        return ThermalState.CRITICAL
    if celsius >= 80:
        return ThermalState.HOT
    if celsius >= 65:
        return ThermalState.WARM
    return ThermalState.NOMINAL


def read_thermal() -> ThermalReading:
    """Read the hottest available thermal sensor, or report UNKNOWN."""
    try:
        import psutil  # type: ignore[import-not-found]

        temps = psutil.sensors_temperatures()  # type: ignore[attr-defined]
    except (ImportError, AttributeError, OSError):
        return ThermalReading(
            ThermalState.UNKNOWN, None, "none",
            "no portable thermal API on this platform (psutil sensors "
            "unavailable); install psutil or inject a provider",
        )
    readings = [
        entry.current
        for entries in temps.values()
        for entry in entries
        if getattr(entry, "current", None) is not None
    ]
    if not readings:
        return ThermalReading(
            ThermalState.UNKNOWN, None, "psutil",
            "psutil present but no thermal sensors exposed",
        )
    hottest = max(readings)
    return ThermalReading(_classify(hottest), float(hottest), "psutil")

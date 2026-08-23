"""CPU capability probing (cores, architecture, frequency when available)."""

from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from typing import Optional

__all__ = ["CPUInfo", "probe_cpu"]


@dataclass(frozen=True)
class CPUInfo:
    """Detected CPU facts; ``None`` means "could not determine"."""

    architecture: str
    logical_cores: int
    physical_cores: Optional[int]
    max_frequency_mhz: Optional[float]


def probe_cpu() -> CPUInfo:
    """Probe CPU facts using stdlib, enriching with psutil when present."""
    physical: Optional[int] = None
    freq: Optional[float] = None
    try:
        import psutil  # type: ignore[import-not-found]

        physical = psutil.cpu_count(logical=False)
        raw_freq = psutil.cpu_freq()
        if raw_freq is not None:
            freq = float(raw_freq.max or raw_freq.current)
    except ImportError:
        pass
    return CPUInfo(
        architecture=platform.machine() or "unknown",
        logical_cores=os.cpu_count() or 1,
        physical_cores=physical,
        max_frequency_mhz=freq,
    )

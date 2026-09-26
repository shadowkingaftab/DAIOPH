"""Anomaly detector (statistical, deterministic)."""

from __future__ import annotations

import statistics
from typing import List

__all__ = ["detect_anomalies"]


def detect_anomalies(values: List[float], z_threshold: float = 2.0) -> List[int]:
    """Return indices of values whose z-score exceeds *z_threshold*.

    Uses population mean/std; returns [] for degenerate inputs.
    """
    if len(values) < 2:
        return []
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values)
    if stdev == 0:
        return []
    return [
        i for i, v in enumerate(values)
        if abs((v - mean) / stdev) > z_threshold
    ]

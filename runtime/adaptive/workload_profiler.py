"""In-memory workload timing profiler.

Records per-workload execution durations and exposes percentile summaries.
Thread-safe; bounded history per workload keeps long-running processes flat.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional

__all__ = ["WorkloadProfiler", "WorkloadStats"]


@dataclass(frozen=True)
class WorkloadStats:
    """Summary statistics for one workload key."""

    workload: str
    samples: int
    mean_ms: float
    p95_ms: float
    max_ms: float


class WorkloadProfiler:
    """Record and summarize execution durations per workload."""

    def __init__(self, history_per_workload: int = 500) -> None:
        if history_per_workload < 1:
            raise ValueError("history_per_workload must be >= 1")
        self._history: Dict[str, Deque[float]] = {}
        self._limit = history_per_workload
        self._lock = threading.Lock()

    def record(self, workload: str, duration_ms: float) -> None:
        """Record one *duration_ms* sample for *workload*."""
        if duration_ms < 0:
            raise ValueError("duration_ms must be non-negative")
        with self._lock:
            bucket = self._history.setdefault(
                workload, deque(maxlen=self._limit)
            )
            bucket.append(duration_ms)

    def timed(self, workload: str):
        """Decorator/context recording wall time of the wrapped call."""
        profiler = self

        class _Timer:
            def __enter__(self_inner):
                self_inner.start = time.perf_counter()
                return self_inner

            def __exit__(self_inner, *exc_info):
                elapsed = (time.perf_counter() - self_inner.start) * 1000.0
                profiler.record(workload, elapsed)

        return _Timer()

    def stats(self, workload: str) -> Optional[WorkloadStats]:
        """Summarize recorded samples, or None when nothing recorded."""
        with self._lock:
            samples: List[float] = sorted(self._history.get(workload, ()))
        if not samples:
            return None
        p95_index = min(len(samples) - 1, int(len(samples) * 0.95))
        return WorkloadStats(
            workload=workload,
            samples=len(samples),
            mean_ms=round(sum(samples) / len(samples), 3),
            p95_ms=round(samples[p95_index], 3),
            max_ms=round(samples[-1], 3),
        )

    def keys(self) -> List[str]:
        """All workload keys with recorded samples."""
        with self._lock:
            return sorted(self._history.keys())

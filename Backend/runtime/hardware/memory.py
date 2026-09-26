"""Memory statistics with psutil enrichment and /proc fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__ = ["MemorySnapshot", "snapshot_memory"]


def _proc_meminfo() -> dict:
    """Parse /proc/meminfo (Linux) into a KiB-keyed dict."""
    values: dict = {}
    try:
        with open("/proc/meminfo", encoding="ascii") as handle:
            for line in handle:
                key, _, rest = line.partition(":")
                parts = rest.split()
                if parts:
                    values[key.strip()] = int(parts[0])
    except (OSError, ValueError):
        pass
    return values


@dataclass(frozen=True)
class MemorySnapshot:
    """Current memory usage; ``None`` fields mean "undetectable here"."""

    total_bytes: Optional[int]
    available_bytes: Optional[int]
    percent_used: Optional[float]


def snapshot_memory() -> MemorySnapshot:
    """Take a memory snapshot via psutil, falling back to /proc/meminfo."""
    try:
        import psutil  # type: ignore[import-not-found]

        vm = psutil.virtual_memory()
        return MemorySnapshot(
            total_bytes=int(vm.total),
            available_bytes=int(vm.available),
            percent_used=float(vm.percent),
        )
    except ImportError:
        info = _proc_meminfo()
        total_kib = info.get("MemTotal")
        if total_kib is None:
            return MemorySnapshot(None, None, None)
        available_kib = info.get("MemAvailable")
        used_ratio = (
            round((total_kib - available_kib) / total_kib * 100.0, 1)
            if available_kib is not None else None
        )
        return MemorySnapshot(
            total_bytes=total_kib * 1024,
            available_bytes=(available_kib * 1024
                             if available_kib is not None else None),
            percent_used=used_ratio,
        )

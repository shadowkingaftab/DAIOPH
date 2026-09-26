"""Storage capacity probing via shutil."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import Dict

__all__ = ["StorageUsage", "probe_storage"]


@dataclass(frozen=True)
class StorageUsage:
    """Disk usage for one path."""

    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int

    @property
    def percent_used(self) -> float:
        """Percentage of the volume in use."""
        if self.total_bytes <= 0:
            return 0.0
        return round(self.used_bytes / self.total_bytes * 100.0, 1)


def probe_storage(path: str = ".") -> StorageUsage:
    """Probe disk usage for *path* (raises OSError for invalid paths)."""
    total, used, free = shutil.disk_usage(path)
    return StorageUsage(path=path, total_bytes=total, used_bytes=used,
                        free_bytes=free)


def probe_storages(paths: Dict[str, str]) -> Dict[str, StorageUsage]:
    """Probe several named paths; failures are reported per-name."""
    results: Dict[str, StorageUsage] = {}
    for name, path in paths.items():
        try:
            results[name] = probe_storage(path)
        except OSError:
            continue
    return results

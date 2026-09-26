"""Core hardware detection using stdlib plus guarded optional imports.

Detection results are facts gathered at call time. Anything that cannot be
determined is reported as ``None``/empty — never guessed.
"""

from __future__ import annotations

import os
import platform
import subprocess  # noqa: S404 - only fixed, allowlisted probe commands
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__all__ = ["HardwareInfo", "HardwareDetector"]


def _read_proc_meminfo_kb() -> Optional[int]:
    """Linux fallback: total memory in KiB from /proc/meminfo."""
    try:
        with open("/proc/meminfo", encoding="ascii") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return None


@dataclass
class HardwareInfo:
    """Snapshot of statically detectable host facts."""

    platform_name: str
    platform_release: str
    architecture: str
    python_version: str
    logical_cpus: int
    total_memory_bytes: Optional[int] = None
    extras: Dict[str, Any] = field(default_factory=dict)


class HardwareDetector:
    """Detects CPU, memory, and OS facts; delegates GPUs to ``runtime.hardware.gpu``."""

    def detect(self) -> HardwareInfo:
        """Gather current host information."""
        mem_bytes: Optional[int] = None
        try:
            import psutil  # type: ignore[import-not-found]

            mem_bytes = int(psutil.virtual_memory().total)
        except ImportError:
            kb = _read_proc_meminfo_kb()
            if kb is not None:
                mem_bytes = kb * 1024
        return HardwareInfo(
            platform_name=platform.system() or "unknown",
            platform_release=platform.release(),
            architecture=platform.machine() or "unknown",
            python_version=platform.python_version(),
            logical_cpus=os.cpu_count() or 1,
            total_memory_bytes=mem_bytes,
        )

    @staticmethod
    def _probe(command: List[str], timeout: float = 3.0) -> Optional[str]:
        """Run an allowlisted probe command; None when unavailable."""
        try:
            result = subprocess.run(  # noqa: S603 - fixed allowlisted argv
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        return result.stdout.strip()

    def summary(self) -> Dict[str, Any]:
        """JSON-friendly summary suitable for logs and dashboards."""
        info = self.detect()
        return {
            "platform": f"{info.platform_name} {info.platform_release}",
            "architecture": info.architecture,
            "python": info.python_version,
            "logical_cpus": info.logical_cpus,
            "total_memory_gb": (
                round(info.total_memory_bytes / 1024**3, 2)
                if info.total_memory_bytes else None
            ),
        }

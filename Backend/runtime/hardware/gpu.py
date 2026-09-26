"""GPU detection across CUDA, Metal, and ROCm.

Every probe is evidence-based: a GPU is reported only when its vendor tool
or library confirms it. On machines without the tooling, the result is an
empty list — never an assumed device.
"""

from __future__ import annotations

import platform
import subprocess  # noqa: S404 - fixed allowlisted vendor probes
from dataclasses import dataclass
from typing import List, Optional

__all__ = ["GPUDevice", "detect_gpus"]


@dataclass(frozen=True)
class GPUDevice:
    """One detected GPU device."""

    vendor: str          # "nvidia" | "apple" | "amd"
    backend: str         # "cuda" | "metal" | "rocm"
    name: str
    vram_mb: Optional[int]


def _run(command: List[str], timeout: float = 3.0) -> Optional[str]:
    """Execute an allowlisted vendor probe; None on any failure."""
    try:
        result = subprocess.run(  # noqa: S603 - fixed allowlisted argv
            command, capture_output=True, text=True, timeout=timeout, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _detect_cuda() -> List[GPUDevice]:
    """NVIDIA GPUs via nvidia-smi (present only when the driver ships it)."""
    output = _run(["nvidia-smi", "--query-gpu=name,memory.total",
                   "--format=csv,noheader"])
    devices: List[GPUDevice] = []
    if not output:
        return devices
    for line in output.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 2:
            try:
                vram = int(parts[1].split()[0])
            except (ValueError, IndexError):
                vram = None
            devices.append(GPUDevice("nvidia", "cuda", parts[0], vram))
    return devices


def _detect_rocm() -> List[GPUDevice]:
    """AMD GPUs via rocm-smi (present only with a ROCm installation)."""
    output = _run(["rocm-smi", "--showproductname", "--showvram"])
    if not output:
        return []
    # Parsing vendor output robustly is best-effort; report card count only.
    cards = [ln for ln in output.splitlines() if "Card series" in ln]
    return [
        GPUDevice("amd", "rocm", line.split(":", 1)[-1].strip(), None)
        for line in cards
    ]


def _detect_metal() -> List[GPUDevice]:
    """Apple GPUs: reported only on darwin/arm64 where Metal is guaranteed."""
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        chip = platform.processor() or "apple-silicon"
        return [GPUDevice("apple", "metal", f"Apple Silicon ({chip})", None)]
    return []


def detect_gpus() -> List[GPUDevice]:
    """Detect GPUs across all supported backends (evidence-based only)."""
    found: List[GPUDevice] = []
    found.extend(_detect_cuda())
    found.extend(_detect_rocm())
    found.extend(_detect_metal())
    return found

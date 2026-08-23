"""Accelerator abstraction over detected GPU backends."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from runtime.hardware.gpu import GPUDevice, detect_gpus

__all__ = ["Accelerator", "available_accelerators"]


@dataclass(frozen=True)
class Accelerator:
    """A usable acceleration target derived from a detected GPU."""

    backend: str
    device_name: str
    vram_mb: Optional[int]

    def supports_batching(self) -> bool:
        """VRAM-backed backends can batch; unified-memory ones conservatively can too."""
        return True


def available_accelerators() -> List[Accelerator]:
    """Return accelerators for every currently detected GPU (may be empty)."""
    return [
        Accelerator(
            backend=device.backend,
            device_name=device.name,
            vram_mb=device.vram_mb,
        )
        for device in detect_gpus()
    ]

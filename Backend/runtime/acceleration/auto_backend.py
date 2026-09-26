"""Automatic backend selection by preference order.

:class:`select_backend` probes GPU backends in preference order and falls
back to CPU. Selection is purely evidence-driven: an unavailable backend is
skipped, and the returned object always truthfully reports itself.
"""

from __future__ import annotations

from typing import Union

from runtime.acceleration.cpu_backend import CpuBackend
from runtime.acceleration.cuda_backend import CudaBackend
from runtime.acceleration.metal_backend import MetalBackend
from runtime.acceleration.rocm_backend import RocmBackend

__all__ = ["select_backend", "AccelerationBackend"]

AccelerationBackend = Union[CudaBackend, MetalBackend, RocmBackend, CpuBackend]

#: Preference order: discrete VRAM first, unified memory next, CPU last.
PREFERENCE = ("cuda", "rocm", "metal")


def select_backend(preference: tuple = PREFERENCE) -> AccelerationBackend:
    """Pick the first available backend, else CPU (never None)."""
    candidates = {
        "cuda": CudaBackend,
        "rocm": RocmBackend,
        "metal": MetalBackend,
    }
    for slug in preference:
        backend_cls = candidates.get(slug)
        if backend_cls is None:
            continue
        backend = backend_cls()
        if backend.available():
            return backend
    return CpuBackend.create()

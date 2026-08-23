"""AMD ROCm acceleration backend.

Availability is determined strictly by runtime evidence (rocm-smi query);
when the check fails, :meth:`available` returns False and nothing claims
acceleration it cannot deliver.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

__all__ = ["RocmBackend"]


@dataclass(frozen=True)
class RocmBackend:
    """AMD ROCm backend gated behind a real availability probe."""

    device_name: Optional[str] = None

    @property
    def name(self) -> str:
        """Backend identifier."""
        return "rocm"

    def available(self) -> bool:
        """True only when the rocm-smi probe succeeds right now."""
        from runtime.hardware.gpu import _detect_rocm

        return bool(_detect_rocm())

    def describe(self) -> Dict[str, Any]:
        """JSON-friendly description (safe to call regardless)."""
        return {
            "backend": self.name,
            "available": self.available(),
            "device": self.device_name,
        }

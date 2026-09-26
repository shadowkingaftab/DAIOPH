"""Apple Metal acceleration backend.

Availability is determined strictly by runtime evidence (Apple-silicon darwin detection);
when the check fails, :meth:`available` returns False and nothing claims
acceleration it cannot deliver.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

__all__ = ["MetalBackend"]


@dataclass(frozen=True)
class MetalBackend:
    """Apple Metal backend gated behind a real availability probe."""

    device_name: Optional[str] = None

    @property
    def name(self) -> str:
        """Backend identifier."""
        return "metal"

    def available(self) -> bool:
        """True only when the darwin/arm64 platform check succeeds right now."""
        from runtime.hardware.gpu import _detect_metal

        return bool(_detect_metal())

    def describe(self) -> Dict[str, Any]:
        """JSON-friendly description (safe to call regardless)."""
        return {
            "backend": self.name,
            "available": self.available(),
            "device": self.device_name,
        }

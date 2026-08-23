"""CPU compute backend — always available, honestly described."""

from __future__ import annotations

import os
from dataclasses import dataclass

__all__ = ["CpuBackend"]


@dataclass(frozen=True)
class CpuBackend:
    """The universal fallback backend."""

    threads: int

    @staticmethod
    def create() -> "CpuBackend":
        """Build a CPU backend sized to the machine."""
        return CpuBackend(threads=max(1, (os.cpu_count() or 1) - 1))

    @property
    def name(self) -> str:
        """Backend identifier."""
        return "cpu"

    def available(self) -> bool:
        """The CPU backend is always available."""
        return True

    def describe(self) -> dict:
        """JSON-friendly description."""
        return {"backend": self.name, "threads": self.threads}

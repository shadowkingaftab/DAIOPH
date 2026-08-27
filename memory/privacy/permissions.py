"""Memory access permissions (deny by default)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet

__all__ = ["MemoryPermissions", "MemoryPermissionError"]


class MemoryPermissionError(PermissionError):
    """Raised when a memory access is not permitted."""


@dataclass(frozen=True)
class MemoryPermissions:
    """Allowed memory operations per subject."""

    allowed_operations: FrozenSet[str] = field(default_factory=frozenset)

    def allows(self, operation: str) -> bool:
        """True only when *operation* is allowed."""
        return operation in self.allowed_operations

    def require(self, operation: str) -> None:
        """Raise :class:`MemoryPermissionError` unless allowed."""
        if not self.allows(operation):
            raise MemoryPermissionError(
                f"memory operation {operation!r} denied by policy"
            )

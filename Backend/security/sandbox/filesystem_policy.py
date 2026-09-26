"""Filesystem sandbox policy (deny by default)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet

__all__ = ["FilesystemPolicy", "FilesystemViolation"]


class FilesystemViolation(PermissionError):
    """Raised when an operation violates the filesystem policy."""


@dataclass(frozen=True)
class FilesystemPolicy:
    """Allowed filesystem capabilities and roots."""

    allowed_capabilities: FrozenSet[str] = field(default_factory=frozenset)
    allowed_roots: FrozenSet[str] = field(default_factory=frozenset)
    read_only: bool = False

    def allows(self, capability: str, path: str) -> bool:
        """True only when capability is allowed and path is under a root."""
        if capability not in self.allowed_capabilities:
            return False
        if self.read_only and capability in {"fs_write", "fs_delete"}:
            return False
        return any(path.startswith(root) for root in self.allowed_roots)

    def require(self, capability: str, path: str) -> None:
        """Raise :class:`FilesystemViolation` unless allowed."""
        if not self.allows(capability, path):
            raise FilesystemViolation(
                f"filesystem {capability} on {path!r} denied by policy"
            )

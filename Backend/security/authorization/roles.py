"""Role definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet

__all__ = ["Role"]


@dataclass(frozen=True)
class Role:
    """A named set of permissions."""

    name: str
    permissions: FrozenSet[str] = field(default_factory=frozenset)

    def allows(self, permission: str) -> bool:
        """True when this role grants *permission*."""
        return permission in self.permissions

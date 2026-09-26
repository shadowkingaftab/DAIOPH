"""Authorization policies (deny by default)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet

from security.authorization.roles import Role

__all__ = ["Policy", "PolicyError"]


class PolicyError(PermissionError):
    """Raised when a subject lacks a required permission."""


@dataclass
class Policy:
    """Maps subjects to roles; permission checks deny by default."""

    roles: Dict[str, Role] = field(default_factory=dict)

    def assign(self, subject: str, role: Role) -> None:
        """Assign *role* to *subject*."""
        self.roles[subject] = role

    def check(self, subject: str, permission: str) -> bool:
        """True only when *subject*'s role grants *permission*."""
        role = self.roles.get(subject)
        return role is not None and role.allows(permission)

    def require(self, subject: str, permission: str) -> None:
        """Raise :class:`PolicyError` unless permitted."""
        if not self.check(subject, permission):
            raise PolicyError(
                f"subject {subject!r} lacks permission {permission!r}"
            )

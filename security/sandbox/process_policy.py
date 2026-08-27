"""Process sandbox policy (deny by default)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet

__all__ = ["ProcessPolicy", "ProcessViolation"]


class ProcessViolation(PermissionError):
    """Raised when a process operation violates the policy."""


@dataclass(frozen=True)
class ProcessPolicy:
    """Allowed process capabilities and command prefixes."""

    allowed_capabilities: FrozenSet[str] = field(default_factory=frozenset)
    allowed_command_prefixes: FrozenSet[str] = field(default_factory=frozenset)

    def allows(self, capability: str, command: str = "") -> bool:
        """True only when capability is allowed and command is permitted."""
        if capability not in self.allowed_capabilities:
            return False
        if command:
            return any(command.startswith(p) for p in self.allowed_command_prefixes)
        return True

    def require(self, capability: str, command: str = "") -> None:
        """Raise :class:`ProcessViolation` unless allowed."""
        if not self.allows(capability, command):
            raise ProcessViolation(
                f"process {capability} on {command!r} denied by policy"
            )

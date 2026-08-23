"""Deny-by-default sandbox gating for task handlers.

A :class:`Sandbox` wraps handler callables so they may only exercise
capabilities explicitly granted by a :class:`SandboxPolicy`. This is a
*capability gate*, not an OS-level sandbox: it gives executors a uniform,
testable enforcement point. OS-level isolation belongs to
``security/sandbox/`` and platform tooling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Iterable, Set

__all__ = ["SandboxPolicy", "Sandbox", "SandboxViolation"]


class SandboxViolation(PermissionError):
    """Raised when a handler attempts a capability it was not granted."""


@dataclass
class SandboxPolicy:
    """Declares what a sandboxed handler may do.

    Attributes:
        allowed_capabilities: Capability names the handler may request.
        read_only: When True, mutating capabilities are rejected even if
            individually listed (defence in depth).
        max_output_items: Upper bound applied to returned list/dict sizes.
    """

    allowed_capabilities: Set[str] = field(default_factory=set)
    read_only: bool = False
    max_output_items: int = 1000

    def allows(self, capability: str) -> bool:
        """True when *capability* is permitted under this policy."""
        if capability not in self.allowed_capabilities:
            return False
        if self.read_only and capability.endswith(("_write", "_delete", "_exec")):
            return False
        return True


# Capabilities with side effects that read_only policies always block.
MUTATING_CAPABILITIES = frozenset(
    {"fs_write", "fs_delete", "process_exec", "net_post", "system_config"}
)


class Sandbox:
    """Enforces a :class:`SandboxPolicy` around handler callables."""

    def __init__(self, policy: SandboxPolicy) -> None:
        self.policy = policy

    def guard(self, capability: str) -> None:
        """Raise :class:`SandboxViolation` unless *capability* is allowed."""
        if capability in MUTATING_CAPABILITIES and self.policy.read_only:
            raise SandboxViolation(
                f"capability {capability!r} is mutating and policy is read-only"
            )
        if not self.policy.allows(capability):
            raise SandboxViolation(f"capability {capability!r} is not granted")

    def wrap(self, capability: str, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Return *fn* guarded behind a capability check."""

        @wraps(fn)
        def guarded(*args: Any, **kwargs: Any) -> Any:
            self.guard(capability)
            output = fn(*args, **kwargs)
            return self._clamp(output)

        return guarded

    def _clamp(self, output: Any) -> Any:
        """Best-effort size clamp so runaway handlers cannot flood memory."""
        limit = self.policy.max_output_items
        if isinstance(output, (list, tuple)) and len(output) > limit:
            return list(output)[:limit]
        if isinstance(output, dict) and len(output) > limit:
            return dict(list(output.items())[:limit])
        return output

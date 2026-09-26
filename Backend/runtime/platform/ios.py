"""iOS platform capabilities.

This module is importable everywhere; :func:`is_current_platform` reports
whether it describes the running OS, and every capability is declared
explicitly so callers degrade gracefully instead of crashing.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import FrozenSet

__all__ = ["PlatformCapabilities", "CAPABILITIES", "is_current_platform",
           "require_capability"]


@dataclass(frozen=True)
class PlatformCapabilities:
    """What this platform supports, declared explicitly."""

    name: str
    supported: FrozenSet[str] = field(default_factory=frozenset)

    def has(self, capability: str) -> bool:
        """True when *capability* is supported here."""
        return capability in self.supported


CAPABILITIES = PlatformCapabilities(
    name='iOS',
    supported=frozenset({'background_fetch'}),
)


def is_current_platform() -> bool:
    """True when running on iOS."""
    return ( sys.platform in {'ios', 'pyodide.ios'} or sys.platform.startswith('iphone') )


def require_capability(capability: str) -> None:
    """Raise :class:`CapabilityUnavailableError` unless supported here."""
    if not CAPABILITIES.has(capability):
        raise CapabilityUnavailableError(
            f"capability {capability!r} is not available on "
            f"{CAPABILITIES.name}"
        )


class CapabilityUnavailableError(RuntimeError):
    """The requested platform capability is unsupported on this OS."""

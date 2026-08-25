"""Basic tool health metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from tools.registry.tool_registry import ToolRegistry

__all__ = ["ToolHealth", "check_tool_health"]


@dataclass(frozen=True)
class ToolHealth:
    """Outcome of a dry health probe for one tool."""

    name: str
    ok: bool
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """JSON-friendly view."""
        return {"name": self.name, "ok": self.ok, "error": self.error}


def check_tool_health(registry: ToolRegistry) -> list:
    """Probe each tool for ``available()`` when defined (False otherwise).

    A tool is considered healthy if it either lacks an availability check
    or the check returns True. Errors are reported per-tool, never raised.
    """
    results = []
    for name in registry.list_tools(include_hidden=True):
        schema = registry.get(name)
        probe = getattr(schema.fn, "available", None)
        if probe is None:
            results.append(ToolHealth(name=name, ok=True))
            continue
        try:
            ok = bool(probe())
        except Exception as exc:  # noqa: BLE001 - report, never crash
            results.append(ToolHealth(name=name, ok=False, error=str(exc)))
            continue
        results.append(ToolHealth(name=name, ok=ok))
    return {"tools": [r.to_dict() for r in results]}

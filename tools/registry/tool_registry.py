"""Thread-safe permissioned tool registry."""

from __future__ import annotations

import threading
from typing import Any, Callable, Dict, Iterable, List, Optional

from tools.registry.tool_schema import ToolPermissionError, ToolSchema

__all__ = ["ToolRegistry"]

ApprovalCallback = Callable[[str, Dict[str, Any]], bool]


class ToolRegistry:
    """Registers tools and invokes them behind permission gates.

    Args:
        allowed_tools: Tool names callable without approval at startup.
        approval_callback: Optional ``(tool_name, kwargs) -> bool`` used for
            destructive tools. Absent callback => destructive denied.
    """

    def __init__(
        self,
        allowed_tools: Optional[Iterable[str]] = None,
        approval_callback: Optional[ApprovalCallback] = None,
    ) -> None:
        self._tools: Dict[str, ToolSchema] = {}
        self._allowed: set = set(allowed_tools or ())
        self._approval_callback = approval_callback
        self._lock = threading.Lock()

    def register(self, schema: ToolSchema) -> None:
        """Register *schema*; later registration replaces earlier."""
        with self._lock:
            self._tools[schema.name] = schema

    def get(self, name: str) -> ToolSchema:
        """Return schema by name.

        Raises:
            KeyError: If unknown.
        """
        with self._lock:
            try:
                return self._tools[name]
            except KeyError:
                raise KeyError(f"unknown tool: {name!r}") from None

    def grant(self, name: str) -> None:
        """Grant unconditional access to *name*."""
        with self._lock:
            self._allowed.add(name)

    def revoke(self, name: str) -> None:
        """Revoke unconditional access to *name*."""
        with self._lock:
            self._allowed.discard(name)

    def invoke(self, name: str, **kwargs: Any) -> Any:
        """Invoke *name* after permission and (if needed) approval checks.

        Raises:
            ToolPermissionError: Denied or approval required but not granted.
        """
        schema = self.get(name)
        args = schema.validate_args(kwargs)
        with self._lock:
            permitted = name in self._allowed
        if not permitted and schema.destructive:
            if self._approval_callback is None or not self._approval_callback(
                name, args
            ):
                raise ToolPermissionError(
                    f"tool {name!r} is destructive and approval was not granted"
                )
        if not permitted and not schema.hidden:
            raise ToolPermissionError(
                f"tool {name!r} is not in allowed_tools"
            )
        return schema.fn(**args)

    def list_tools(self, include_hidden: bool = False) -> List[str]:
        """Names of discoverable tools."""
        with self._lock:
            return sorted(
                n for n, s in self._tools.items()
                if include_hidden or not s.hidden
            )

    def count(self) -> int:
        """Number of registered tools."""
        with self._lock:
            return len(self._tools)

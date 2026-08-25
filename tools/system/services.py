"""Service introspection (Windows-only sc query, graceful elsewhere)."""

from __future__ import annotations

import subprocess
import sys
from typing import List

from tools.registry.tool_schema import ToolSchema

__all__ = ["list_services", "sys_services"]


def list_services(fragment: str = "") -> List[str]:
    """Return matching Windows service names (empty elsewhere)."""
    if sys.platform != "win32":
        return []
    try:
        result = subprocess.run(  # noqa: S603 - fixed allowlisted probe
            ["sc", "query", "type=", "service", "state=", "all"],
            capture_output=True, text=True, timeout=10.0, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    names = [ln[28:].strip() for ln in result.stdout.splitlines()
             if ln.startswith("SERVICE_NAME:")]
    if fragment:
        names = [n for n in names if fragment.lower() in n.lower()]
    return names


sys_services = ToolSchema(
    name="sys_services",
    description="List Windows service names (best-effort)",
    fn=list_services,
    params={"fragment": str},
)

"""System introspection tool."""

from __future__ import annotations

import os
import platform
from typing import Any, Dict

from tools.registry.tool_schema import ToolSchema

__all__ = ["get_system_info", "sys_info"]


def get_system_info() -> Dict[str, Any]:
    """OS/platform facts plus CPU count (stdlib only)."""
    try:
        import psutil  # type: ignore[import-not-found]

        memory = psutil.virtual_memory()
        memory_gb = {"total_gb": round(memory.total / 1024**3, 2)}
    except ImportError:
        memory_gb = {"total_gb": None}
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "cpu_count": os.cpu_count() or 1,
        **memory_gb,
    }


sys_info = ToolSchema(
    name="sys_info",
    description="Read-only OS/platform/CPU/memory facts",
    fn=get_system_info,
)

"""Process listing tool (read-only)."""

from __future__ import annotations

from typing import Any, Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["list_processes", "sys_ps"]


def list_processes(query: str = "") -> List[Dict[str, Any]]:
    """Return pid+name for matching processes using psutil if present."""
    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError:
        return []
    table = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            row = {"pid": proc.info["pid"], "name": proc.info["name"]}
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if not query or query.lower() in row["name"].lower():
            table.append(row)
    return table


sys_ps = ToolSchema(
    name="sys_ps",
    description="List processes whose names match a query",
    fn=list_processes,
    params={"query": str},
)

"""Safe file read tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.registry.tool_schema import ToolSchema

__all__ = ["read_file", "fs_read"]


def read_file(path: str, encoding: str = "utf-8", limit: int = 0) -> str:
    """Read *path*; `limit` > 0 caps the number of characters returned."""
    text = Path(path).read_text(encoding=encoding)
    return text[:limit] if limit > 0 else text


fs_read = ToolSchema(
    name="fs_read",
    description="Read a text file (optionally truncated by char limit)",
    fn=read_file,
    params={"path": str, "encoding": str, "limit": int},
)

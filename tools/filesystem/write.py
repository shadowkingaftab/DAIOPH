"""Write tool — destructive; requires explicit approval."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.registry.tool_schema import ToolSchema

__all__ = ["write_file", "fs_write"]


def write_file(path: str, content: str, encoding: str = "utf-8") -> str:
    """Overwrite *path* with *content*; parents are created if missing."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding=encoding)
    return f"wrote {len(content)} chars to {path}"


fs_write = ToolSchema(
    name="fs_write",
    description="Write/overwrite a file (destructive; requires approval)",
    fn=write_file,
    params={"path": str, "content": str, "encoding": str},
    destructive=True,
)

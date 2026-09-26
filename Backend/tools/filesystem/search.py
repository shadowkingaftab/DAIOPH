"""Filename/glob search tool."""

from __future__ import annotations

from pathlib import Path
from typing import List

from tools.registry.tool_schema import ToolSchema

__all__ = ["search_files", "fs_search"]


def search_files(root: str, glob: str = "*", limit: int = 100) -> List[str]:
    """Return up to *limit* paths under *root* matching *glob*."""
    base = Path(root)
    if not base.is_dir():
        return []
    results = sorted(str(p) for p in base.rglob(glob) if p.is_file())
    return results[:limit]


fs_search = ToolSchema(
    name="fs_search",
    description="Glob search for files beneath a directory",
    fn=search_files,
    params={"root": str, "glob": str, "limit": int},
)

"""File organizer — destructive; requires approval."""

from __future__ import annotations

from pathlib import Path
from typing import List

from tools.registry.tool_schema import ToolSchema

__all__ = ["organize_files", "fs_organize"]


def organize_files(root: str, by: str = "ext") -> List[str]:
    """Move files under *root* into subfolders by extension.

    Returns the list of created directories.
    """
    root_path = Path(root)
    if by != "ext":
        raise ValueError(f"unsupported organizer {by!r}; only 'ext' is supported")
    created: List[str] = []
    for item in root_path.iterdir():
        if item.is_file() and item.suffix:
            folder = root_path / item.suffix.lstrip(".").lower()
            folder.mkdir(exist_ok=True)
            target = folder / item.name
            if not target.exists():
                item.rename(target)
                created.append(str(target))
    return created


fs_organize = ToolSchema(
    name="fs_organize",
    description="Move files into extension-based subfolders (destructive)",
    fn=organize_files,
    params={"root": str, "by": str},
    destructive=True,
)

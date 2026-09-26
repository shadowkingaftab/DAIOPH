"""File metadata probe tool."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from tools.registry.tool_schema import ToolSchema

__all__ = ["get_metadata", "fs_metadata"]


def get_metadata(path: str) -> Dict[str, Any]:
    """Collect size, mtime, and type metadata for *path*."""
    stat = os.stat(path)
    return {
        "path": path,
        "exists": True,
        "size_bytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_dir": Path(path).is_dir(),
    }


fs_metadata = ToolSchema(
    name="fs_metadata",
    description="Return stat metadata for a path",
    fn=get_metadata,
    params={"path": str},
)

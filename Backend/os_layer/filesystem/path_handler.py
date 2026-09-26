from __future__ import annotations

from typing import Dict


class PathHandler:
    """Handles path operations and normalization."""

    @staticmethod
    def normalize(path: str) -> str:
        """Normalize a file path."""
        # Remove double slashes
        while "//" in path:
            path = path.replace("//", "/")
        # Ensure trailing slash for directories
        if path and not path.endswith("/"):
            path += "/"
        return path

    @staticmethod
    def join(*paths: str) -> str:
        """Join multiple path components."""
        result = ""
        for p in paths:
            p = p.strip("/")
            if result:
                result += "/" + p
            else:
                result = p
        return PathHandler.normalize(result)

    @staticmethod
    def is_absolute(path: str) -> bool:
        """Check if a path is absolute."""
        return path.startswith("/")

    @staticmethod
    def get_filename(path: str) -> str:
        """Extract filename from path."""
        parts = path.rstrip("/").split("/")
        return parts[-1] if parts else ""

    @staticmethod
    def get_directory(path: str) -> str:
        """Extract directory from path."""
        path = path.rstrip("/")
        idx = path.rfind("/")
        return path[:idx] if idx >= 0 else "/"
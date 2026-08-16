from __future__ import annotations

from typing import Dict, List


class FilesystemManager:
    """Manages filesystem operations."""

    def __init__(self) -> None:
        self.mounts: Dict[str, str] = {}
        self.current_dir: str = "/"

    def mount(self, mount_point: str, path: str) -> bool:
        """Mount a filesystem path."""
        if mount_point in self.mounts:
            return False
        self.mounts[mount_point] = path
        return True

    def unmount(self, mount_point: str) -> bool:
        """Unmount a filesystem path."""
        if mount_point not in self.mounts:
            return False
        del self.mounts[mount_point]
        return True

    def change_dir(self, path: str) -> bool:
        """Change the current working directory."""
        if path == "/":
            self.current_dir = "/"
            return True
        # Simplified path handling
        if path.startswith("/"):
            self.current_dir = path
        elif path == "..":
            # Go up one directory
            parts = self.current_dir.rstrip("/").split("/")
            if len(parts) > 1:
                self.current_dir = "/".join(parts[:-1]) + "/"
            else:
                self.current_dir = "/"
        else:
            # Relative path
            self.current_dir = self.current_dir.rstrip("/") + "/" + path
        return True

    def get_current_dir(self) -> str:
        """Return the current working directory."""
        return self.current_dir

    def list_dir(self, path: str = "") -> List[str]:
        """List directory contents."""
        target = path if path else self.current_dir
        # Return simulated directory listing
        return [f"{target}/file1", f"{target}/file2", f"{target}/subdir"]

    def exists(self, path: str) -> bool:
        """Check if a path exists."""
        return True  # Simplified for demo
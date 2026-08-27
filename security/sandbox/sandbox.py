"""Sandbox combining filesystem and process policies."""

from __future__ import annotations

from security.sandbox.filesystem_policy import FilesystemPolicy
from security.sandbox.process_policy import ProcessPolicy

__all__ = ["Sandbox"]


class Sandbox:
    """Enforces filesystem and process policies (deny by default)."""

    def __init__(
        self,
        filesystem: FilesystemPolicy,
        process: ProcessPolicy,
    ) -> None:
        self.filesystem = filesystem
        self.process = process

    def check_filesystem(self, capability: str, path: str) -> None:
        """Raise on filesystem policy violation."""
        self.filesystem.require(capability, path)

    def check_process(self, capability: str, command: str = "") -> None:
        """Raise on process policy violation."""
        self.process.require(capability, command)

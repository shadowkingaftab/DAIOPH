from __future__ import annotations

from typing import Any, Dict


class ProtocolVersion:
    """Manages protocol version compatibility."""

    def __init__(self, version: str = "1.0") -> None:
        self.version = version
        self.supported_versions: list[str] = ["1.0"]

    def register_version(self, version: str) -> None:
        """Register a supported protocol version."""
        if version not in self.supported_versions:
            self.supported_versions.append(version)

    def is_compatible(self, version: str) -> bool:
        """Check if a version is compatible with the current protocol."""
        return version in self.supported_versions

    def get_version_info(self) -> Dict[str, Any]:
        """Return protocol version information."""
        return {
            "current": self.version,
            "supported": list(self.supported_versions),
        }
"""Installation identity management for the DAIOPH system."""

import hashlib
import os
import platform
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class InstallationIdentity:
    """Represents a unique DAIOPH installation."""

    installation_id: str
    created_at: str
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def generate(cls, version: str = "1.0.0") -> "InstallationIdentity":
        """Generate a new installation identity.

        Args:
            version: DAIOPH version.

        Returns:
            InstallationIdentity: New installation identity.
        """
        import datetime

        # Build a stable unique identifier from machine-specific data
        raw = f"{platform.node()}|{platform.system()}|{platform.machine()}"
        installation_id = hashlib.sha256(raw.encode()).hexdigest()[:16]

        return cls(
            installation_id=installation_id,
            created_at=datetime.datetime.utcnow().isoformat(),
            version=version,
            metadata={
                "platform": platform.system(),
                "machine": platform.machine(),
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Returns:
            Dict[str, Any]: Serialized installation.
        """
        return {
            "installation_id": self.installation_id,
            "created_at": self.created_at,
            "version": self.version,
            "metadata": self.metadata,
        }
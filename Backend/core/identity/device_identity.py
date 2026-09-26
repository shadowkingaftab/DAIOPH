"""Device identity management for the DAIOPH system."""

import platform
import socket
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class DeviceIdentity:
    """Represents the identity of the device running DAIOPH."""

    device_id: str
    hostname: str
    platform: str
    architecture: str
    python_version: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def detect(cls) -> "DeviceIdentity":
        """Detect the current device identity.

        Returns:
            DeviceIdentity: Detected device identity.
        """
        return cls(
            device_id=str(uuid.uuid4()),
            hostname=socket.gethostname(),
            platform=platform.system(),
            architecture=platform.machine(),
            python_version=platform.python_version(),
            metadata={
                "node": platform.node(),
                "release": platform.release(),
                "processor": platform.processor(),
            },
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Returns:
            Dict[str, Any]: Serialized identity.
        """
        return {
            "device_id": self.device_id,
            "hostname": self.hostname,
            "platform": self.platform,
            "architecture": self.architecture,
            "python_version": self.python_version,
            "metadata": self.metadata,
        }
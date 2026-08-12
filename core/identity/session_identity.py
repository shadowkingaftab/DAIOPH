"""Session identity management for the DAIOPH system."""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class SessionIdentity:
    """Represents a runtime session in the DAIOPH system."""

    session_id: str
    device_id: str = ""
    user_id: str = ""
    created_at: str = ""
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, device_id: str = "", user_id: str = "") -> "SessionIdentity":
        """Create a new session identity.

        Args:
            device_id: Associated device ID.
            user_id: Associated user ID.

        Returns:
            SessionIdentity: New session identity.
        """
        import datetime

        return cls(
            session_id=str(uuid.uuid4()),
            device_id=device_id,
            user_id=user_id,
            created_at=datetime.datetime.utcnow().isoformat(),
        )

    def is_expired(self) -> bool:
        """Check if the session is expired.

        Returns:
            bool: True if expired.
        """
        if not self.expires_at:
            return False
        import datetime

        expiry = datetime.datetime.fromisoformat(self.expires_at)
        return datetime.datetime.utcnow() > expiry

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Returns:
            Dict[str, Any]: Serialized session.
        """
        return {
            "session_id": self.session_id,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
        }
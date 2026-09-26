"""User identity management for the DAIOPH system."""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class UserIdentity:
    """Represents a user of the DAIOPH system."""

    user_id: str
    name: str = ""
    email: str = ""
    preferences: Dict[str, Any] = field(default_factory=dict)
    roles: List[str] = field(default_factory=list)
    created_at: str = ""

    @classmethod
    def create(cls, name: str = "", email: str = "") -> "UserIdentity":
        """Create a new user identity.

        Args:
            name: User display name.
            email: User email.

        Returns:
            UserIdentity: New user identity.
        """
        import datetime

        return cls(
            user_id=str(uuid.uuid4()),
            name=name,
            email=email,
            created_at=datetime.datetime.utcnow().isoformat(),
        )

    def set_preference(self, key: str, value: Any) -> None:
        """Set a user preference.

        Args:
            key: Preference key.
            value: Preference value.
        """
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference.

        Args:
            key: Preference key.
            default: Default value if not set.

        Returns:
            Any: Preference value.
        """
        return self.preferences.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Returns:
            Dict[str, Any]: Serialized identity.
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "preferences": self.preferences,
            "roles": self.roles,
            "created_at": self.created_at,
        }
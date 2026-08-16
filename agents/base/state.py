from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AgentState:
    """Represents the current state of an agent.

    Attributes:
        status: Current status of the agent (e.g. idle, running, stopped).
        data: Arbitrary state data associated with the agent.
        last_updated: Timestamp of the last state update.
    """

    status: str = "idle"
    data: Dict[str, Any] = field(default_factory=dict)
    last_updated: Optional[float] = None

    def update(self, **kwargs: Any) -> None:
        """Update state fields with the given keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of the state."""
        return {
            "status": self.status,
            "data": self.data,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Create an AgentState instance from a dictionary."""
        return cls(
            status=data.get("status", "idle"),
            data=data.get("data", {}),
            last_updated=data.get("last_updated"),
        )
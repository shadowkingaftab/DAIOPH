from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Message:
    """A message exchanged between federated participants."""

    msg_type: str
    sender: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of the message."""
        return {
            "type": self.msg_type,
            "sender": self.sender,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create a Message from a dictionary."""
        return cls(
            msg_type=data["type"],
            sender=data["sender"],
            payload=data.get("payload", {}),
        )
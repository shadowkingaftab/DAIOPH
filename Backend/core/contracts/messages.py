"""Message definitions for the DAIOPH system."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """A message exchanged between system components."""

    role: str  # "user", "assistant", "system"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_id: str = ""


class MessageBuilder:
    """Helper for building system messages."""

    @staticmethod
    def system(content: str, **metadata: Any) -> Message:
        """Create a system message.

        Args:
            content: Message content.
            **metadata: Additional metadata.

        Returns:
            Message: System message.
        """
        return Message(role="system", content=content, metadata=metadata)

    @staticmethod
    def user(content: str, **metadata: Any) -> Message:
        """Create a user message.

        Args:
            content: Message content.
            **metadata: Additional metadata.

        Returns:
            Message: User message.
        """
        return Message(role="user", content=content, metadata=metadata)

    @staticmethod
    def assistant(content: str, **metadata: Any) -> Message:
        """Create an assistant message.

        Args:
            content: Message content.
            **metadata: Additional metadata.

        Returns:
            Message: Assistant message.
        """
        return Message(role="assistant", content=content, metadata=metadata)
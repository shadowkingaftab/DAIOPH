"""ConversationBuffer - buffers conversation history."""

from typing import Any, Dict, List, Optional


class ConversationBuffer:
    """Buffers conversation messages for short-term recall."""

    def __init__(self, max_messages: int = 50) -> None:
        """Initialize the conversation buffer.

        Args:
            max_messages: Maximum messages to retain.
        """
        self._max_messages = max_messages
        self._messages: List[Dict[str, Any]] = []

    def add(self, role: str, content: str) -> None:
        """Add a message to the buffer.

        Args:
            role: Message role (user/assistant).
            content: Message content.
        """
        if len(self._messages) >= self._max_messages:
            self._messages.pop(0)
        self._messages.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all buffered messages.

        Returns:
            List[Dict[str, Any]]: Buffered messages.
        """
        return list(self._messages)

    def clear(self) -> None:
        """Clear the buffer."""
        self._messages = []

</final_file_content>
</write_to_file></tool_call>
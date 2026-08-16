from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """Base class for all DAIOPH agents.

    Provides common infrastructure including:
    - State management
    - Goal tracking
    - Memory storage
    - Lifecycle hooks (start, stop, reset)
    """

    def __init__(self, agent_id: str, **kwargs: Any) -> None:
        self.agent_id = agent_id
        self._state: Dict[str, Any] = {}
        self._goals: Dict[str, Any] = {}
        self._memory: Dict[str, Any] = {}
        self._initialized = False

    @property
    def state(self) -> Dict[str, Any]:
        """Return the current agent state."""
        return self._state

    @state.setter
    def state(self, value: Dict[str, Any]) -> None:
        self._state = value

    @property
    def goals(self) -> Dict[str, Any]:
        """Return the current goals."""
        return self._goals

    @goals.setter
    def goals(self, value: Dict[str, Any]) -> None:
        self._goals = value

    @property
    def memory(self) -> Dict[str, Any]:
        """Return the current memory."""
        return self._memory

    @memory.setter
    def memory(self, value: Dict[str, Any]) -> None:
        self._memory = value

    @abstractmethod
    def start(self) -> None:
        """Start the agent execution loop."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Stop the agent execution loop."""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Reset the agent to initial state."""
        raise NotImplementedError

    def update(self, delta: float) -> None:
        """Update agent state by delta seconds.

        Args:
            delta: Time elapsed since last update, in seconds.
        """
        pass

    def can_handle(self, message_type: str) -> bool:
        """Check if this agent can handle a given message type.

        Args:
            message_type: The type of message to check.

        Returns:
            True if the agent can handle this message type.
        """
        return False

    def handle_message(
        self, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle an incoming message.

        Args:
            message: The message dictionary to process.

        Returns:
            Optional response message, or None if not handled.
        """
        return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.agent_id}>"
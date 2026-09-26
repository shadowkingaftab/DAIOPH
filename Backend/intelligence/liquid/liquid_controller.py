"""Liquid controller - decides actions based on liquid state."""

from typing import Any, Dict, List, Optional


class LiquidController:
    """Controls the behavior of the liquid intelligence system.

    The controller maps state snapshots to actions, using a
    configurable policy that can be updated through adaptation.
    """

    def __init__(self) -> None:
        """Initialize the liquid controller."""
        self._policy: Dict[str, Any] = {}
        self._action_history: List[Dict[str, Any]] = []
        self._default_action: str = "process"

    def decide(self, state_snapshot: Dict[str, Any]) -> str:
        """Decide an action based on the current state.

        Args:
            state_snapshot: Current state snapshot.

        Returns:
            str: Action name.
        """
        # Simple policy: use stability to decide action
        stability = state_snapshot.get("stability", 1.0)
        if stability < 0.3:
            action = "stabilize"
        elif stability < 0.7:
            action = "adapt"
        else:
            action = self._default_action

        self._action_history.append({"state": state_snapshot, "action": action})
        return action

    def set_policy(self, key: str, value: Any) -> None:
        """Set a policy value.

        Args:
            key: Policy key.
            value: Policy value.
        """
        self._policy[key] = value

    def get_policy(self, key: str, default: Any = None) -> Any:
        """Get a policy value.

        Args:
            key: Policy key.
            default: Default if not found.

        Returns:
            Any: Policy value or default.
        """
        return self._policy.get(key, default)

    def get_action_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get action history.

        Args:
            limit: Optional number of recent entries.

        Returns:
            List[Dict[str, Any]]: Action history.
        """
        if limit:
            return self._action_history[-limit:]
        return list(self._action_history)

    def reset(self) -> None:
        """Reset the controller."""
        self._policy = {}
        self._action_history = []
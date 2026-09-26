"""UserAdaptation - adapts to user behavior patterns."""

from typing import Any, Dict, List, Optional


class UserAdaptation:
    """Adapts system behavior based on user interaction patterns."""

    def __init__(self) -> None:
        """Initialize user adaptation."""
        self._preferences: Dict[str, Any] = {}
        self._interaction_history: List[Dict[str, Any]] = []
        self._limit = 100

    def record_interaction(self, interaction: Dict[str, Any]) -> None:
        """Record a user interaction.

        Args:
            interaction: Interaction details.
        """
        self._interaction_history.append(interaction)
        if len(self._interaction_history) > self._limit:
            self._interaction_history = self._interaction_history[-self._limit:]

    def update_preference(self, key: str, value: Any) -> None:
        """Update a user preference.

        Args:
            key: Preference key.
            value: Preference value.
        """
        self._preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference.

        Args:
            key: Preference key.
            default: Default if not found.

        Returns:
            Any: Preference value.
        """
        return self._preferences.get(key, default)

    def get_behavior_profile(self) -> Dict[str, Any]:
        """Get the user's behavior profile.

        Returns:
            Dict[str, Any]: Behavior profile.
        """
        return {
            "preferences": dict(self._preferences),
            "interaction_count": len(self._interaction_history),
        }

    def reset(self) -> None:
        """Reset user adaptation."""
        self._preferences = {}
        self._interaction_history = []

</final_file_content>
</write_to_file>
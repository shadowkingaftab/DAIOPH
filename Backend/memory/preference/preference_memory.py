"""PreferenceMemory - stores user preferences."""

from typing import Any, Dict, Optional


class PreferenceMemory:
    """Stores user preferences."""

    def __init__(self) -> None:
        """Initialize preference memory."""
        self._preferences: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Set a preference.

        Args:
            key: Preference key.
            value: Preference value.
        """
        self._preferences[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a preference.

        Args:
            key: Preference key.
            default: Default if not found.

        Returns:
            Any: Preference value.
        """
        return self._preferences.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all preferences.

        Returns:
            Dict[str, Any]: All preferences.
        """
        return dict(self._preferences)

</final_file_content>
</write_to_file></tool_call>
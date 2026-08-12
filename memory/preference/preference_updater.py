"""PreferenceUpdater - updates user preferences."""

from typing import Any, Dict, Optional


class PreferenceUpdater:
    """Updates user preferences based on feedback."""

    def __init__(self) -> None:
        """Initialize the preference updater."""
        self._updates: List[Dict[str, Any]] = []
        self._limit = 100

    def update(self, key: str, value: Any, source: str = "user") -> None:
        """Update a preference.

        Args:
            key: Preference key.
            value: New value.
            source: Source of update.
        """
        self._updates.append({"key": key, "value": value, "source": source})
        if len(self._updates) > self._limit:
            self._updates = self._updates[-self._limit:]

    def get_history(self) -> List[Dict[str, Any]]:
        """Get update history.

        Returns:
            List[Dict[str, Any]]: Update history.
        """
        return list(self._updates)

</final_file_content>
</write_to_file></tool_call>
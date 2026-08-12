"""EventStore - stores events for episodic memory."""

from typing import Any, Dict, List, Optional


class EventStore:
    """Stores events for episodic memory retrieval."""

    def __init__(self) -> None:
        """Initialize the event store."""
        self._events: List[Dict[str, Any]] = []

    def add(self, event: Dict[str, Any]) -> None:
        """Add an event.

        Args:
            event: Event data.
        """
        self._events.append(event)

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all events.

        Returns:
            List[Dict[str, Any]]: All events.
        """
        return list(self._events)

    def query(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Query events by field.

        Args:
            field: Field name.
            value: Field value.

        Returns:
            List[Dict[str, Any]]: Matching events.
        """
        return [e for e in self._events if e.get(field) == value]

</final_file_content>
</write_to_file></tool_call>
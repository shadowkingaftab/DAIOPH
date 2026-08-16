from __future__ import annotations

from typing import Any, Dict, List


class EventBus:
    """Event bus for inter-component communication."""

    def __init__(self) -> None:
        self.subscribers: Dict[str, List[Any]] = {}
        self.events: List[Dict[str, Any]] = []

    def subscribe(self, event_type: str, handler: Any) -> None:
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event: Dict[str, Any]) -> None:
        """Publish an event to all subscribers."""
        event_type = event.get("type", "")
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(event)
        self.events.append(event)

    def get_events(self) -> List[Dict[str, Any]]:
        """Return all published events."""
        return list(self.events)
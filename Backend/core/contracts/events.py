"""Event definitions for the DAIOPH system."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Event:
    """A system event."""

    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    timestamp: Optional[float] = None


class EventBus:
    """Publish/subscribe event bus."""

    def __init__(self) -> None:
        """Initialize the event bus."""
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Event type.
            handler: Handler callable.
        """
        self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Event type.
            handler: Handler to remove.
        """
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers.

        Args:
            event: Event to publish.
        """
        for handler in self._subscribers.get(event.type, []):
            try:
                handler(event)
            except Exception as e:  # pragma: no cover
                print(f"[EventBus] Subscriber error for '{event.type}': {e}")

    def has_subscribers(self, event_type: str) -> bool:
        """Check if an event type has subscribers.

        Args:
            event_type: Event type.

        Returns:
            bool: True if subscribers exist.
        """
        return bool(self._subscribers.get(event_type))
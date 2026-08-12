"""Event loop - asynchronous task and event processing for the DAIOPH kernel."""

import queue
import threading
import time
from typing import Any, Callable, Dict, List, Optional


class EventLoop:
    """Simple event loop for processing tasks and events.

    Provides a thread-safe queue-based event processing system
    with support for scheduled and recurring tasks.
    """

    def __init__(self) -> None:
        """Initialize the event loop."""
        self._queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        self._handlers: Dict[str, Callable[..., Any]] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._scheduled: List[Dict[str, Any]] = []

    def register_handler(self, event_type: str, handler: Callable[..., Any]) -> None:
        """Register a handler for an event type.

        Args:
            event_type: Event type string.
            handler: Callable to invoke for the event.
        """
        self._handlers[event_type] = handler

    def post(self, event_type: str, data: Any = None) -> None:
        """Post an event to the queue.

        Args:
            event_type: Event type string.
            data: Optional event payload.
        """
        self._queue.put({"type": event_type, "data": data, "time": time.time()})

    def schedule(self, event_type: str, delay: float, data: Any = None) -> None:
        """Schedule an event to fire after a delay.

        Args:
            event_type: Event type string.
            delay: Delay in seconds.
            data: Optional event payload.
        """
        self._scheduled.append({
            "type": event_type,
            "data": data,
            "fire_at": time.time() + delay,
        })

    def start(self) -> None:
        """Start the event loop in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="event-loop")
        self._thread.start()

    def stop(self) -> None:
        """Stop the event loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self) -> None:
        """Main event loop processing."""
        while self._running:
            # Process scheduled events
            now = time.time()
            due = [e for e in self._scheduled if e["fire_at"] <= now]
            self._scheduled = [e for e in self._scheduled if e["fire_at"] > now]
            for event in due:
                self._dispatch(event["type"], event["data"])

            # Process queued events
            try:
                event = self._queue.get(timeout=0.1)
                self._dispatch(event["type"], event["data"])
            except queue.Empty:
                pass

    def _dispatch(self, event_type: str, data: Any) -> None:
        """Dispatch an event to its handler.

        Args:
            event_type: Event type string.
            data: Event payload.
        """
        handler = self._handlers.get(event_type)
        if handler:
            try:
                handler(data)
            except Exception as e:  # pragma: no cover
                print(f"[EventLoop] Handler error for '{event_type}': {e}")

    @property
    def is_running(self) -> bool:
        """Whether the event loop is running."""
        return self._running

    def pending_count(self) -> int:
        """Get the number of pending queued events.

        Returns:
            int: Pending event count.
        """
        return self._queue.qsize()
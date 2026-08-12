"""Intent registry - manages intent definitions and handlers."""

from typing import Any, Callable, Dict, List, Optional


class IntentRegistry:
    """Registry for intent definitions and their handlers."""

    def __init__(self) -> None:
        """Initialize the intent registry."""
        self._handlers: Dict[str, Callable] = {}
        self._intents: Dict[str, Dict[str, Any]] = {}

    def register(self, intent: Any) -> None:
        """Register an intent definition.

        Args:
            intent: Intent definition with 'name' and 'handler' keys.
        """
        name = getattr(intent, "name", None) or intent.get("name")
        if not name:
            return
        self._handlers[name] = getattr(intent, "handler", None) or intent.get("handler")
        self._intents[name] = {"name": name, **(intent or {})}

    def get_handler(self, intent_name: str) -> Optional[Callable]:
        """Get a handler for an intent.

        Args:
            intent_name: Name of the intent.

        Returns:
            Optional[Callable]: Handler callable, or None.
        """
        return self._handlers.get(intent_name)

    def list_intents(self) -> List[str]:
        """List all registered intent names.

        Returns:
            List[str]: Registered intent names.
        """
        return list(self._handlers.keys())

    def unregister(self, intent_name: str) -> None:
        """Unregister an intent.

        Args:
            intent_name: Name of the intent to remove.
        """
        self._handlers.pop(intent_name, None)
        self._intents.pop(intent_name, None)
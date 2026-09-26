"""Intent engine - orchestrates intent classification and handling."""

from typing import Any, Dict, List, Optional

from intelligence.intent.intent_classifier import IntentClassifier
from intelligence.intent.intent_registry import IntentRegistry
from intelligence.intent.intent_schema import IntentSchema


class IntentEngine:
    """Coordinates the intent detection pipeline.

    The engine combines the classifier, registry, and schema to
    detect intents from text and dispatch to handlers.
    """

    def __init__(self, registry: Optional[IntentRegistry] = None,
                 classifier: Optional[IntentClassifier] = None) -> None:
        """Initialize the intent engine.

        Args:
            registry: Optional intent registry.
            classifier: Optional intent classifier.
        """
        self.registry = registry or IntentRegistry()
        self.classifier = classifier or IntentClassifier()
        self.schema = IntentSchema()

    def detect(self, text: str) -> Dict[str, Any]:
        """Detect the intent of a text input.

        Args:
            text: Input text.

        Returns:
            Dict[str, Any]: Detection result with intent and confidence.
        """
        return self.classifier.classify(text)

    def handle(self, text: str, context: Optional[Dict[str, Any]] = None):
        """Detect intent and dispatch to its handler.

        Args:
            text: Input text.
            context: Optional context.

        Returns:
            Any: Handler result.
        """
        result = self.detect(text)
        intent_name = result.get("intent")
        handler = self.registry.get_handler(intent_name)
        if handler:
            return handler(text, context or {})
        return {"error": f"No handler for intent '{intent_name}'"}

    def register_intent(self, intent: Any) -> None:
        """Register an intent definition.

        Args:
            intent: Intent definition object.
        """
        self.registry.register(intent)

    def list_intents(self) -> List[str]:
        """List all registered intents.

        Returns:
            List[str]: Intent names.
        """
        return self.registry.list_intents()
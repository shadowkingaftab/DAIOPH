"""Intent classifier - lightweight rule- and ML-based intent classification."""

from typing import Any, Dict, List, Optional


class IntentClassifier:
    """Classifies text into intent categories.

    Uses keyword matching as a lightweight baseline, with a
    pluggable ML model hook for production use.
    """

    def __init__(self, model: Optional[Any] = None) -> None:
        """Initialize the intent classifier.

        Args:
            model: Optional ML model for classification.
        """
        self._model = model
        self._keywords: Dict[str, List[str]] = {
            "greeting": ["hello", "hi", "hey", "good morning", "good evening"],
            "farewell": ["bye", "goodbye", "see you", "exit", "quit"],
            "help": ["help", "how do", "what can", "support"],
            "summarize": ["summarize", "summary", "condense"],
            "translate": ["translate", "convert to", "in spanish", "in hindi"],
            "code": ["code", "function", "program", "write a script", "bug"],
        }
        self._default_intent = "general"

    def classify(self, text: str) -> Dict[str, Any]:
        """Classify a text input.

        Args:
            text: Input text.

        Returns:
            Dict[str, Any]: Result with intent and confidence.
        """
        text_lower = text.lower()

        # Rule-based keyword matching
        best_intent = self._default_intent
        best_score = 0.0
        for intent, keywords in self._keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower) / len(keywords)
            if score > best_score:
                best_score = score
                best_intent = intent

        # If ML model available, use it for higher-confidence prediction
        if self._model is not None:
            try:
                result = self._model.predict([text])
                best_intent = str(result[0])
                best_score = max(best_score, 0.8)
            except Exception:
                pass

        confidence = 0.5 + (best_score * 0.5)
        return {"intent": best_intent, "confidence": min(1.0, max(0.0, confidence))}

    def set_model(self, model: Any) -> None:
        """Set the ML model for classification.

        Args:
            model: ML model instance.
        """
        self._model = model

    def get_intents(self) -> List[str]:
        """Get all known intents.

        Returns:
            List[str]: Intent names.
        """
        return list(self._keywords.keys()) + [self._default_intent]
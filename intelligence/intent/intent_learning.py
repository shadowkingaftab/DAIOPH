"""Intent learning - continual learning mechanisms for intent evolution."""

from typing import Any, Dict, List, Optional


class IntentLearner:
    """Learns from intent interactions and evolves classification rules."""

    def __init__(self, classifier: Optional[Any] = None) -> None:
        """Initialize the intent learner.

        Args:
            classifier: Optional classifier to update.
        """
        self._classifier = classifier
        self._corpus: List[Dict[str, Any]] = []
        self._corpus_limit = 1000

    def learn(self, text: str, intent: str, outcome: str = "correct") -> None:
        """Learn from a classification interaction.

        Args:
            text: The input text.
            intent: The intent label.
            outcome: The classification outcome.
        """
        record = {"text": text, "intent": intent, "outcome": outcome}
        self._corpus.append(record)
        if len(self._corpus) > self._corpus_limit:
            self._corpus = self._corpus[-self._corpus_limit:]

    def update_classifier(self, classifier: Any) -> None:
        """Update the underlying classifier with learned data.

        Args:
            classifier: Classifier instance to update.
        """
        self._classifier = classifier

    def get_corpus(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the learning corpus.

        Args:
            limit: Optional number of recent entries.

        Returns:
            List[Dict[str, Any]]: Learning records.
        """
        if limit:
            return self._corpus[-limit:]
        return list(self._corpus)

    def get_stats(self) -> Dict[str, Any]:
        """Get learning statistics.

        Returns:
            Dict[str, Any]: Statistics.
        """
        return {
            "total_examples": len(self._corpus),
            "unique_intents": len(set(r["intent"] for r in self._corpus)) if self._corpus else 0,
        }
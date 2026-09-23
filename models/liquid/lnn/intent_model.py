"""Intent model: liquid encoder + nearest-prototype classifier head."""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from models.liquid.lnn.architecture import LiquidNetwork

__all__ = ["LiquidIntentModel"]


class LiquidIntentModel:
    """Deterministic intent classifier over liquid dynamics.

    Text is encoded to a scalar signal (mean character code, normalized),
    pushed through a liquid network, and the final hidden state is matched
    against per-intent prototypes learned from labeled examples. No ML
    framework or network access is involved.
    """

    def __init__(self, layer_taus: Sequence[float] = (1.0, 2.0)) -> None:
        self.network = LiquidNetwork(layer_taus)
        self._prototypes: Dict[str, List[float]] = {}
        self._examples: Dict[str, List[float]] = {}

    @staticmethod
    def encode(text: str) -> float:
        """Deterministic scalar encoding of text into [-1, 1]."""
        if not text:
            return 0.0
        codes = [ord(ch) for ch in text]
        mean_code = sum(codes) / len(codes)
        return (mean_code - 96.0) / 32.0  # ~[-1, 1] for lowercase text

    def add_example(self, text: str, intent: str) -> None:
        """Record a labeled example for prototype estimation."""
        self.network.reset()
        states = self.network.forward([self.encode(text)])
        final = states[-1][-1] if states and states[-1] else 0.0
        self._examples.setdefault(intent, []).append(final)

    def fit(self) -> None:
        """(Re)compute per-intent prototype means from examples."""
        self._prototypes = {
            intent: [sum(vals) / len(vals)]
            for intent, vals in self._examples.items()
        }

    def predict(self, text: str) -> Tuple[Optional[str], float]:
        """Predict (intent, confidence); (None, 0.0) when unfitted."""
        if not self._prototypes:
            return None, 0.0
        self.network.reset()
        states = self.network.forward([self.encode(text)])
        final = states[-1][-1] if states and states[-1] else 0.0
        best_intent: Optional[str] = None
        best_distance = float("inf")
        for intent, proto in self._prototypes.items():
            distance = abs(final - proto[0])
            if distance < best_distance:
                best_distance = distance
                best_intent = intent
        confidence = 1.0 / (1.0 + best_distance)
        return best_intent, confidence

    def num_intents(self) -> int:
        """Number of fitted intents."""
        return len(self._prototypes)

from __future__ import annotations

from typing import Dict


class TrustManager:
    """Manages trust levels for federated clients."""

    def __init__(self) -> None:
        self.trust_scores: Dict[str, float] = {}

    def set_trust(self, client_id: str, score: float) -> None:
        """Set the trust score for a client."""
        self.trust_scores[client_id] = max(0.0, min(1.0, score))

    def adjust_trust(self, client_id: str, delta: float) -> None:
        """Adjust the trust score for a client."""
        current = self.trust_scores.get(client_id, 0.5)
        self.set_trust(client_id, current + delta)

    def get_trust(self, client_id: str) -> float:
        """Return the trust score for a client."""
        return self.trust_scores.get(client_id, 0.5)

    def is_trusted(self, client_id: str, threshold: float = 0.7) -> bool:
        """Check if a client is trusted above a threshold."""
        return self.get_trust(client_id) >= threshold

    def get_all_trust(self) -> Dict[str, float]:
        """Return all trust scores."""
        return dict(self.trust_scores)
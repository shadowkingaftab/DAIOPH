from __future__ import annotations

from typing import Dict


class ContributionScore:
    """Tracks and computes contribution scores for clients."""

    def __init__(self) -> None:
        self.scores: Dict[str, float] = {}

    def update_score(self, client_id: str, delta: float) -> None:
        """Update the contribution score for a client."""
        self.scores[client_id] = self.scores.get(client_id, 0.0) + delta

    def get_score(self, client_id: str) -> float:
        """Return the contribution score for a client."""
        return self.scores.get(client_id, 0.0)

    def get_all_scores(self) -> Dict[str, float]:
        """Return all contribution scores."""
        return dict(self.scores)

    def reset(self, client_id: str) -> None:
        """Reset the score for a client."""
        self.scores[client_id] = 0.0

    def get_ranking(self) -> list[tuple[str, float]]:
        """Return clients ranked by contribution score."""
        return sorted(
            self.scores.items(), key=lambda x: x[1], reverse=True
        )
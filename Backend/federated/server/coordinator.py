from __future__ import annotations

from typing import Any, Dict, List


class Coordinator:
    """Coordinates training rounds across federated clients."""

    def __init__(self) -> None:
        self.round: int = 0
        self.max_rounds: int = 10
        self.participants: List[str] = []
        self.round_results: List[Dict[str, Any]] = []

    def set_max_rounds(self, max_rounds: int) -> None:
        """Set the maximum number of training rounds."""
        self.max_rounds = max_rounds

    def select_participants(self, client_ids: List[str]) -> List[str]:
        """Select clients to participate in the next round."""
        self.participants = list(client_ids)
        return self.participants

    def start_round(self) -> int:
        """Start a new training round."""
        if self.round >= self.max_rounds:
            return -1
        self.round += 1
        return self.round

    def record_result(self, result: Dict[str, Any]) -> None:
        """Record the result of a training round."""
        self.round_results.append(result)

    def is_complete(self) -> bool:
        """Check if training is complete."""
        return self.round >= self.max_rounds

    def get_summary(self) -> Dict[str, Any]:
        """Return a summary of the coordination."""
        return {
            "round": self.round,
            "max_rounds": self.max_rounds,
            "participants": self.participants,
            "results_count": len(self.round_results),
            "complete": self.is_complete(),
        }
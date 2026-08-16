from __future__ import annotations

from typing import Any, Dict


class Contribution:
    """Tracks a client's contribution to federated learning."""

    def __init__(self, client_id: str) -> None:
        self.client_id = client_id
        self.data_samples: int = 0
        self.rounds_contributed: int = 0
        self.total_contribution: float = 0.0

    def record_contribution(self, samples: int, weight: float = 1.0) -> None:
        """Record a contribution from this client."""
        self.data_samples += samples
        self.rounds_contributed += 1
        self.total_contribution += samples * weight

    def get_contribution_score(self) -> float:
        """Return the total contribution score."""
        return self.total_contribution

    def get_summary(self) -> Dict[str, Any]:
        """Return a summary of the client's contribution."""
        return {
            "client_id": self.client_id,
            "data_samples": self.data_samples,
            "rounds_contributed": self.rounds_contributed,
            "total_contribution": self.total_contribution,
        }
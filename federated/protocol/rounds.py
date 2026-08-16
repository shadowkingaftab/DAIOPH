from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Round:
    """Represents a single federated training round."""

    round_number: int
    participants: List[str] = field(default_factory=list)
    status: str = "pending"
    results: Dict[str, Any] = field(default_factory=dict)

    def start(self) -> None:
        """Mark the round as in progress."""
        self.status = "in_progress"

    def complete(self, results: Dict[str, Any]) -> None:
        """Mark the round as complete with results."""
        self.status = "completed"
        self.results = results

    def fail(self, reason: str) -> None:
        """Mark the round as failed."""
        self.status = "failed"
        self.results = {"reason": reason}

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of the round."""
        return {
            "round_number": self.round_number,
            "participants": self.participants,
            "status": self.status,
            "results": self.results,
        }
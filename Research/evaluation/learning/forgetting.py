from __future__ import annotations


class ForgettingTracker:
    """Tracks model forgetting events."""

    def __init__(self) -> None:
        self.forgetting_events: list[dict[str, any]] = []

    def record(self, task: str, before: float, after: float) -> None:
        """Record a forgetting event."""
        self.forgetting_events.append({
            "task": task,
            "before": before,
            "after": after,
            "loss": before - after,
        })

    def get_forgetting_summary(self) -> dict[str, any]:
        """Return a summary of forgetting events."""
        if not self.forgetting_events:
            return {"total": 0}
        total_loss = sum(e["loss"] for e in self.forgetting_events)
        return {
            "total": len(self.forgetting_events),
            "total_loss": total_loss,
            "average_loss": total_loss / len(self.forgetting_events),
        }

    def reset(self) -> None:
        """Reset the tracker."""
        self.forgetting_events.clear()
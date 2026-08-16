from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class GoalStatus(Enum):
    """Status of a goal."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Goal:
    """Represents a goal that an agent is working towards.

    Attributes:
        goal_id: Unique identifier for the goal.
        description: Human-readable description of the goal.
        status: Current status of the goal.
        priority: Priority level (higher is more important).
        subtasks: List of sub-goal identifiers.
        metadata: Arbitrary metadata associated with the goal.
    """

    goal_id: str
    description: str
    status: GoalStatus = GoalStatus.PENDING
    priority: int = 0
    subtasks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_in_progress(self) -> None:
        """Mark the goal as in progress."""
        self.status = GoalStatus.IN_PROGRESS

    def mark_completed(self) -> None:
        """Mark the goal as completed."""
        self.status = GoalStatus.COMPLETED

    def mark_failed(self) -> None:
        """Mark the goal as failed."""
        self.status = GoalStatus.FAILED

    def mark_cancelled(self) -> None:
        """Mark the goal as cancelled."""
        self.status = GoalStatus.CANCELLED

    def add_subtask(self, subtask_id: str) -> None:
        """Add a sub-goal identifier to this goal."""
        self.subtasks.append(subtask_id)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of the goal."""
        return {
            "goal_id": self.goal_id,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority,
            "subtasks": self.subtasks,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Goal":
        """Create a Goal instance from a dictionary."""
        return cls(
            goal_id=data["goal_id"],
            description=data["description"],
            status=GoalStatus(data.get("status", "pending")),
            priority=data.get("priority", 0),
            subtasks=data.get("subtasks", []),
            metadata=data.get("metadata", {}),
        )
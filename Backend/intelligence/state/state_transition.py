"""StateTransition - handles state transition logic."""

from typing import Any, Dict, List, Optional


class StateTransition:
    """Handles state transition logic between different states."""

    def __init__(self) -> None:
        """Initialize state transition."""
        self._transitions: Dict[str, List[str]] = {}
        self._current_path: List[str] = []

    def add_transition(self, from_state: str, to_states: List[str]) -> None:
        """Add a transition from one state to others.

        Args:
            from_state: Source state.
            to_states: List of possible target states.
        """
        if from_state not in self._transitions:
            self._transitions[from_state] = []
        self._transitions[from_state].extend(to_states)

    def can_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a transition is allowed.

        Args:
            from_state: Source state.
            to_state: Target state.

        Returns:
            bool: True if transition allowed.
        """
        allowed = self._transitions.get(from_state, [])
        return to_state in allowed

    def get_possible_transitions(self, from_state: str) -> List[str]:
        """Get possible transitions from a state.

        Args:
            from_state: Source state.

        Returns:
            List[str]: Possible target states.
        """
        return self._transitions.get(from_state, [])

    def record_transition(self, from_state: str, to_state: str) -> None:
        """Record a transition that was taken.

        Args:
            from_state: Source state.
            to_state: Target state.
        """
        self._current_path.append({"from": from_state, "to": to_state})

    def get_transition_path(self) -> List[Dict[str, Any]]:
        """Get the transition path.

        Returns:
            List[Dict[str, Any]]: Transition history.
        """
        return list(self._current_path)

    def reset(self) -> None:
        """Reset state transition."""
        self._transitions = {}
        self._current_path = []

</final_file_content>
</write_to_file>
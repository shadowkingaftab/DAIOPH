"""ProceduralReasoning - reasoning over procedural knowledge."""

from typing import Any, Dict, List, Optional


class ProceduralReasoning:
    """Reasons over procedural knowledge (sequences, steps, workflows)."""

    def __init__(self) -> None:
        """Initialize procedural reasoning."""
        self._procedures: Dict[str, List[Dict[str, Any]]] = {}
        self._current_step: Dict[str, Any] = {}

    def register_procedure(self, name: str, steps: List[Dict[str, Any]]) -> None:
        """Register a procedure with its steps.

        Args:
            name: Procedure name.
            steps: List of step descriptions.
        """
        self._procedures[name] = steps

    def execute_step(self, procedure: str, step_index: int) -> Optional[Dict[str, Any]]:
        """Execute a specific step of a procedure.

        Args:
            procedure: Procedure name.
            step_index: Index of the step.

        Returns:
            Optional[Dict[str, Any]]: Step details or None.
        """
        procedure_steps = self._procedures.get(procedure)
        if not procedure_steps:
            return None
        if step_index < 0 or step_index >= len(procedure_steps):
            return None
        return procedure_steps[step_index]

    def get_next_step(self, procedure: str, current_step: int) -> Optional[Dict[str, Any]]:
        """Get the next step in a procedure.

        Args:
            procedure: Procedure name.
            current_step: Current step index.

        Returns:
            Optional[Dict[str, Any]]: Next step or None.
        """
        procedure_steps = self._procedures.get(procedure)
        if not procedure_steps:
            return None
        next_idx = current_step + 1
        if next_idx >= len(procedure_steps):
            return None
        return procedure_steps[next_idx]

    def get_all_steps(self, procedure: str) -> Optional[List[Dict[str, Any]]]:
        """Get all steps of a procedure.

        Args:
            procedure: Procedure name.

        Returns:
            Optional[List[Dict[str, Any]]]: Procedure steps or None.
        """
        return self._procedures.get(procedure)

    def reset(self) -> None:
        """Reset procedural reasoning."""
        self._procedures = {}
        self._current_step = {}

</final_file_content>
</write_to_file>
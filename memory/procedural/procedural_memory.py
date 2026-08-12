"""ProceduralMemory - stores procedural knowledge."""

from typing import Any, Dict, List, Optional


class ProceduralMemory:
    """Stores procedural knowledge (skills, workflows)."""

    def __init__(self) -> None:
        """Initialize procedural memory."""
        self._procedures: Dict[str, List[Dict[str, Any]]] = {}

    def store(self, name: str, steps: List[Dict[str, Any]]) -> None:
        """Store a procedure.

        Args:
            name: Procedure name.
            steps: Procedure steps.
        """
        self._procedures[name] = steps

    def retrieve(self, name: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve a procedure.

        Args:
            name: Procedure name.

        Returns:
            Optional[List[Dict[str, Any]]]: Procedure steps or None.
        """
        return self._procedures.get(name)

    def list_procedures(self) -> List[str]:
        """List all procedure names.

        Returns:
            List[str]: Procedure names.
        """
        return list(self._procedures.keys())

</final_file_content>
</write_to_file></tool_call>
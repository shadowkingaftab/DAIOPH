"""WorkflowStore - stores workflows for procedural memory."""

from typing import Any, Dict, List, Optional


class WorkflowStore:
    """Stores workflows for procedural memory."""

    def __init__(self) -> None:
        """Initialize the workflow store."""
        self._workflows: Dict[str, Dict[str, Any]] = {}

    def add(self, name: str, workflow: Dict[str, Any]) -> None:
        """Add a workflow.

        Args:
            name: Workflow name.
            workflow: Workflow definition.
        """
        self._workflows[name] = workflow

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a workflow.

        Args:
            name: Workflow name.

        Returns:
            Optional[Dict[str, Any]]: Workflow or None.
        """
        return self._workflows.get(name)

    def list_workflows(self) -> List[str]:
        """List all workflow names.

        Returns:
            List[str]: Workflow names.
        """
        return list(self._workflows.keys())

</final_file_content>
</write_to_file></tool_call>
"""CapabilityEvolution - evolves system capabilities."""

from typing import Any, Dict, Optional


class CapabilityEvolution:
    """Evolves system capabilities over time."""

    def __init__(self) -> None:
        """Initialize capability evolution."""
        self._capabilities: Dict[str, Any] = {}
        self._evolution_history: List[Dict[str, Any]] = []
        self._limit = 50

    def add_capability(self, name: str, capability: Any) -> None:
        """Add a capability to evolve.

        Args:
            name: Capability name.
            capability: Capability definition.
        """
        self._capabilities[name] = capability

    def evolve_capability(self, name: str, improvement: Dict[str, Any]) -> None:
        """Evolve a specific capability.

        Args:
            name: Capability name.
            improvement: Improvement specifications.
        """
        if name in self._capabilities:
            self._capabilities[name].update(improvement)
            self._evolution_history.append(
                {"capability": name, "improvement": improvement}
            )
            if len(self._evolution_history) > self._limit:
                self._evolution_history = self._evolution_history[-self._limit:]

    def get_capability(self, name: str) -> Any:
        """Get a capability.

        Args:
            name: Capability name.

        Returns:
            Any: Capability definition.
        """
        return self._capabilities.get(name)

    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Get evolution history.

        Returns:
            List[Dict[str, Any]]: History of improvements.
        """
        return list(self._evolution_history)

</final_file_content>
</write_to_file>
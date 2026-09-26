"""Adaptation manager - handles adaptive behavior for liquid intelligence."""

from typing import Any, Dict, List, Optional


class AdaptationManager:
    """Manages adaptive behavior of the liquid intelligence system.

    Tracks adaptation events and applies adaptive strategies based
    on observed outcomes.
    """

    def __init__(self) -> None:
        """Initialize the adaptation manager."""
        self._adaptations: List[Dict[str, Any]] = []
        self._strategies: Dict[str, Any] = {}
        self._max_history = 500

    def adapt(self, input_data: Any, outcome: Any) -> None:
        """Apply adaptation based on an observed outcome.

        Args:
            input_data: Input that triggered adaptation.
            outcome: Resulting outcome/action.
        """
        record = {
            "input": input_data,
            "outcome": outcome,
            "version": self._adaptations_count() + 1,
        }
        self._adaptations.append(record)
        if len(self._adaptations) > self._max_history:
            self._adaptations = self._adaptations[-self._max_history:]

    def _adaptations_count(self) -> int:
        """Get the number of adaptations applied.

        Returns:
            int: Adaptation count.
        """
        return len(self._adaptations)

    def register_strategy(self, name: str, strategy: Any) -> None:
        """Register an adaptation strategy.

        Args:
            name: Strategy name.
            strategy: Strategy callable/object.
        """
        self._strategies[name] = strategy

    def get_strategy(self, name: str, default: Any = None) -> Any:
        """Get a registered strategy.

        Args:
            name: Strategy name.
            default: Default if not found.

        Returns:
            Any: Strategy or default.
        """
        return self._strategies.get(name, default)

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get adaptation history.

        Args:
            limit: Optional number of recent entries.

        Returns:
            List[Dict[str, Any]]: Adaptation history.
        """
        if limit:
            return self._adaptations[-limit:]
        return list(self._adaptations)

    def get_stats(self) -> Dict[str, Any]:
        """Get adaptation statistics.

        Returns:
            Dict[str, Any]: Statistics.
        """
        return {
            "total_adaptations": len(self._adaptations),
            "strategies": list(self._strategies.keys()),
        }
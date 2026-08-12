"""StrategyAdaptation - adapts learning strategies."""

from typing import Any, Dict, List, Optional


class StrategyAdaptation:
    """Adapts learning strategies based on performance feedback."""

    def __init__(self) -> None:
        """Initialize strategy adaptation."""
        self._strategies: Dict[str, Any] = {}
        self._performance_history: List[Dict[str, Any]] = []
        self._limit = 50

    def register_strategy(self, name: str, strategy: Any) -> None:
        """Register a learning strategy.

        Args:
            name: Strategy name.
            strategy: Strategy instance.
        """
        self._strategies[name] = strategy

    def select_strategy(self, context: Dict[str, Any]) -> Optional[Any]:
        """Select a strategy based on context.

        Args:
            context: Selection context.

        Returns:
            Optional[Any]: Selected strategy or None.
        """
        # Simple selection: return first available
        if self._strategies:
            return list(self._strategies.values())[0]
        return None

    def record_performance(self, strategy: str, performance: Dict[str, Any]) -> None:
        """Record strategy performance.

        Args:
            strategy: Strategy name.
            performance: Performance metrics.
        """
        self._performance_history.append({"strategy": strategy, "performance": performance})
        if len(self._performance_history) > self._limit:
            self._performance_history = self._performance_history[-self._limit:]

    def get_best_strategy(self) -> Optional[str]:
        """Get the best-performing strategy name.

        Returns:
            Optional[str]: Best strategy name.
        """
        if not self._performance_history:
            return None
        # Return strategy with highest success rate
        best = self._performance_history[0]
        best_rate = best.get("performance", {}).get("success_rate", 0)
        for entry in self._performance_history[1:]:
            rate = entry.get("performance", {}).get("success_rate", 0)
            if rate > best_rate:
                best = entry
                best_rate = rate
        return best["strategy"]

    def get_adaptation_stats(self) -> Dict[str, Any]:
        """Get adaptation statistics.

        Returns:
            Dict[str, Any]: Statistics.
        """
        return {
            "total_strategies": len(self._strategies),
            "recorded_performances": len(self._performance_history),
        }

    def reset(self) -> None:
        """Reset strategy adaptation."""
        self._strategies = {}
        self._performance_history = []

</final_file_content>
</write_to_file>
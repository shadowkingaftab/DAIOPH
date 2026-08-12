"""RegressionGuard - prevents performance regression."""

from typing import Any, Dict, Optional


class RegressionGuard:
    """Guards against performance regression during evolution."""

    def __init__(self, threshold: float = 0.95) -> None:
        """Initialize regression guard.

        Args:
            threshold: Performance threshold (0-1).
        """
        self._threshold = threshold
        self._baseline: Optional[float] = None
        self._history: List[float] = []

    def set_baseline(self, performance: float) -> None:
        """Set the baseline performance.

        Args:
            performance: Baseline performance metric.
        """
        self._baseline = performance
        self._history.append(performance)

    def check_regression(self, current: float) -> bool:
        """Check if current performance represents regression.

        Args:
            current: Current performance metric.

        Returns:
            bool: True if regression detected.
        """
        if self._baseline is None:
            return False
        regression = current < self._baseline * self._threshold
        if regression:
            self._history.append(current)
        return regression

    def get_history(self) -> List[float]:
        """Get performance history.

        Returns:
            List[float]: History of performance metrics.
        """
        return list(self._history)

</final_file_content>
</write_to_file>
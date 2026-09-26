"""Validation of task outputs prior to synthesis."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from orchestration.execution.task_executor import TaskResult

__all__ = ["OutputValidator"]


class OutputValidator:
    """Structural validation rules applied to individual task outputs."""

    def validate(
        self,
        value: Any,
        expect_type: Optional[type] = None,
        allow_empty: bool = False,
        max_length: Optional[int] = None,
    ) -> Tuple[bool, List[str]]:
        """Validate *value* against simple structural constraints.

        Args:
            value: The output to check.
            expect_type: Required Python type, when given.
            allow_empty: Whether empty strings/collections pass.
            max_length: Maximum string length, when given.

        Returns:
            ``(ok, problems)`` where *problems* lists human-readable issues.
        """
        problems: List[str] = []
        if expect_type is not None and not isinstance(value, expect_type):
            problems.append(
                f"expected {expect_type.__name__}, got {type(value).__name__}"
            )
        if not allow_empty:
            if isinstance(value, str) and not value.strip():
                problems.append("output is an empty string")
            elif isinstance(value, (list, tuple, dict)) and len(value) == 0:
                problems.append("output is empty")
        if isinstance(value, str) and max_length is not None and len(value) > max_length:
            problems.append(f"output length {len(value)} exceeds {max_length}")
        return (not problems, problems)

    def validate_results(
        self, results: Dict[str, TaskResult]
    ) -> Dict[str, List[str]]:
        """Validate every successful result; returns task_id → problems."""
        report: Dict[str, List[str]] = {}
        for task_id, result in results.items():
            if result.ok:
                ok, problems = self.validate(result.output)
                if not ok:
                    report[task_id] = problems
        return report

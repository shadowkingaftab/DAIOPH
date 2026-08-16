from __future__ import annotations

from typing import Any, Dict, List


class Validator:
    """Validates client updates before aggregation."""

    def __init__(self) -> None:
        self.validation_results: List[Dict[str, Any]] = []

    def validate(self, update: Dict[str, Any]) -> bool:
        """Validate a client update.

        Returns:
            True if the update is valid, False otherwise.
        """
        if not isinstance(update, dict):
            return False
        if not update:
            return False
        result = {"valid": True, "reason": "ok"}
        self.validation_results.append(result)
        return True

    def validate_all(self, updates: List[Dict[str, Any]]) -> List[bool]:
        """Validate a list of updates."""
        return [self.validate(u) for u in updates]

    def get_results(self) -> List[Dict[str, Any]]:
        """Return all validation results."""
        return list(self.validation_results)

    def clear(self) -> None:
        """Clear validation results."""
        self.validation_results.clear()
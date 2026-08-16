from __future__ import annotations

from typing import Any, Dict, List


class ConflictResolver:
    """Resolves state conflicts between distributed nodes."""

    def __init__(self) -> None:
        self.conflicts: List[Dict[str, Any]] = []
        self.resolutions: List[Dict[str, Any]] = []

    def detect(
        self, local: Dict[str, Any], remote: Dict[str, Any]
    ) -> List[str]:
        """Detect conflicting keys between local and remote state."""
        conflicts = []
        for key in local:
            if key in remote and local[key] != remote[key]:
                conflicts.append(key)
        return conflicts

    def resolve(
        self, local: Dict[str, Any], remote: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflicts between local and remote state.

        Local state takes precedence on conflicts.
        """
        merged = dict(remote)
        merged.update(local)
        conflict_keys = self.detect(local, remote)
        if conflict_keys:
            self.conflicts.append({"keys": conflict_keys})
            self.resolutions.append({"resolved": conflict_keys})
        return merged

    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Return all recorded conflicts."""
        return list(self.conflicts)

    def clear(self) -> None:
        """Clear all recorded conflicts and resolutions."""
        self.conflicts.clear()
        self.resolutions.clear()
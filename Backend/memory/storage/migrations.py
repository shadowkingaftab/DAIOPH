"""Migrations - database schema migrations."""

from typing import Any, Dict, List, Optional


class Migrations:
    """Manages database schema migrations."""

    def __init__(self) -> None:
        """Initialize migrations."""
        self._migrations: List[Dict[str, Any]] = []
        self._applied: List[str] = []

    def add(self, version: str, migration_fn: Any) -> None:
        """Add a migration.

        Args:
            version: Migration version.
            migration_fn: Migration function.
        """
        self._migrations.append({"version": version, "fn": migration_fn})

    def apply(self, version: str) -> bool:
        """Apply a migration.

        Args:
            version: Migration version.

        Returns:
            bool: True if applied.
        """
        for m in self._migrations:
            if m["version"] == version and version not in self._applied:
                m["fn"]()
                self._applied.append(version)
                return True
        return False

    def get_applied(self) -> List[str]:
        """Get applied migration versions.

        Returns:
            List[str]: Applied versions.
        """
        return list(self._applied)

</final_file_content>
</write_to_file></tool_call>
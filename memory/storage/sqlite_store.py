"""SqliteStore - SQLite-backed memory storage."""

from typing import Any, Dict, List, Optional


class SqliteStore:
    """SQLite-backed memory storage."""

    def __init__(self, db_path: str = "memory.db") -> None:
        """Initialize the SQLite store.

        Args:
            db_path: Path to SQLite database.
        """
        self._db_path = db_path
        self._data: Dict[str, Any] = {}

    def put(self, key: str, value: Any) -> None:
        """Store a value.

        Args:
            key: Storage key.
            value: Value to store.
        """
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value.

        Args:
            key: Storage key.
            default: Default if not found.

        Returns:
            Any: Stored value.
        """
        return self._data.get(key, default)

    def delete(self, key: str) -> None:
        """Delete a value.

        Args:
            key: Storage key.
        """
        self._data.pop(key, None)

    def get_db_path(self) -> str:
        """Get the database path.

        Returns:
            str: Database path.
        """
        return self._db_path

</final_file_content>
</write_to_file></tool_call>
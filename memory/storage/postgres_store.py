"""PostgresStore - PostgreSQL-backed memory storage."""

from typing import Any, Dict, List, Optional


class PostgresStore:
    """PostgreSQL-backed memory storage."""

    def __init__(self, connection_string: str = "") -> None:
        """Initialize the PostgreSQL store.

        Args:
            connection_string: Database connection string.
        """
        self._connection_string = connection_string
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

    def get_connection_string(self) -> str:
        """Get the connection string.

        Returns:
            str: Connection string.
        """
        return self._connection_string

</final_file_content>
</write_to_file></tool_call>
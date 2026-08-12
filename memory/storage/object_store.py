"""ObjectStore - object-based memory storage."""

from typing import Any, Dict, List, Optional


class ObjectStore:
    """Object-based memory storage."""

    def __init__(self, bucket: str = "memory") -> None:
        """Initialize the object store.

        Args:
            bucket: Storage bucket name.
        """
        self._bucket = bucket
        self._objects: Dict[str, Any] = {}

    def put(self, key: str, obj: Any) -> None:
        """Store an object.

        Args:
            key: Object key.
            obj: Object to store.
        """
        self._objects[key] = obj

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve an object.

        Args:
            key: Object key.
            default: Default if not found.

        Returns:
            Any: Stored object.
        """
        return self._objects.get(key, default)

    def delete(self, key: str) -> None:
        """Delete an object.

        Args:
            key: Object key.
        """
        self._objects.pop(key, None)

    def list_objects(self) -> List[str]:
        """List all object keys.

        Returns:
            List[str]: Object keys.
        """
        return list(self._objects.keys())

</final_file_content>
</write_to_file></tool_call>
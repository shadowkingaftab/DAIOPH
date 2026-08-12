"""ModelMetadata - metadata container for model definitions."""

from typing import Any, Dict, Optional


class ModelMetadata:
    """Stores metadata for a model definition."""

    def __init__(self, name: str, version: str, description: str = "") -> None:
        """Initialize model metadata.

        Args:
            name: Model name.
            version: Model version.
            description: Optional description.
        """
        self.name = name
        self.version = version
        self.description = description
        self._extra: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        """Set an extra metadata field.

        Args:
            key: Field key.
            value: Field value.
        """
        self._extra[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get an extra metadata field.

        Args:
            key: Field key.
            default: Default if not found.

        Returns:
            Any: Field value.
        """
        return self._extra.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict.

        Returns:
            Dict[str, Any]: Serialized metadata.
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "extra": dict(self._extra),
        }

</final_file_content>
</write_to_file>
"""Intent schema - defines the structure of intent definitions."""

from typing import Any, Dict, List, Optional


class IntentSchema:
    """Schema for validating intent definitions.

    Ensures that intent definitions have the required fields
    and follow the expected structure.
    """

    REQUIRED_FIELDS = {"name"}

    @classmethod
    def validate(cls, definition: Any) -> bool:
        """Validate an intent definition.

        Args:
            definition: Intent definition to validate.

        Returns:
            bool: True if valid.
        """
        if isinstance(definition, dict):
            return cls.REQUIRED_FIELDS.issubset(definition.keys())
        if hasattr(definition, "name"):
            return cls.REQUIRED_FIELDS.issubset(definition.__dict__.keys())
        return False

    @classmethod
    def extract_fields(cls, definition: Any) -> Dict[str, Any]:
        """Extract the standard fields from a definition.

        Args:
            definition: Intent definition.

        Returns:
            Dict[str, Any]: Extracted fields.
        """
        if isinstance(definition, dict):
            return {k: definition[k] for k in cls.REQUIRED_FIELDS if k in definition}
        if hasattr(definition, "name"):
            return {"name": definition.name}
        return {}


class SchemaRegistry:
    """Registry for tracked schemas."""

    def __init__(self) -> None:
        """Initialize the schema registry."""
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, schema: Dict[str, Any]) -> None:
        """Register a schema.

        Args:
            name: Schema name.
            schema: Schema dict.
        """
        self._schemas[name] = schema

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a schema by name.

        Args:
            name: Schema name.

        Returns:
            Optional[Dict[str, Any]]: Schema or None.
        """
        return self._schemas.get(name)
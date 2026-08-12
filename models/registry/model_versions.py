"""ModelVersions - tracks model version history."""

from typing import Any, Dict, List, Optional


class ModelVersions:
    """Tracks version history for a model."""

    def __init__(self, model_name: str) -> None:
        """Initialize version tracking.

        Args:
            model_name: Name of the model.
        """
        self._model_name = model_name
        self._versions: List[Dict[str, Any]] = []

    def add_version(self, version: str, metadata: Dict[str, Any]) -> None:
        """Add a version entry.

        Args:
            version: Version string.
            metadata: Version metadata.
        """
        self._versions.append({"version": version, "metadata": metadata})

    def get_latest(self) -> Optional[Dict[str, Any]]:
        """Get the latest version.

        Returns:
            Optional[Dict[str, Any]]: Latest version entry.
        """
        return self._versions[-1] if self._versions else None

    def get_version(self, version: str) -> Optional[Dict[str, Any]]:
        """Get a specific version.

        Args:
            version: Version string.

        Returns:
            Optional[Dict[str, Any]]: Version entry or None.
        """
        for v in self._versions:
            if v["version"] == version:
                return v
        return None

    def list_versions(self) -> List[str]:
        """List all version strings.

        Returns:
            List[str]: Version strings.
        """
        return [v["version"] for v in self._versions]

</final_file_content>
</write_to_file></tool_call>
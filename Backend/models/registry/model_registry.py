"""ModelRegistry - manages model registration and lookup."""

from typing import Any, Dict, List, Optional


class ModelRegistry:
    """Registry for managing model definitions and versions."""

    def __init__(self) -> None:
        """Initialize the model registry."""
        self._models: Dict[str, Dict[str, Any]] = {}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}

    def register(self, name: str, version: str, metadata: Dict[str, Any],
                 capabilities: Optional[Dict[str, Any]] = None) -> None:
        """Register a model.

        Args:
            name: Model name.
            version: Model version.
            metadata: Model metadata dict.
            capabilities: Optional capability dict.
        """
        if name not in self._models:
            self._models[name] = {}
        self._models[name][version] = {
            "metadata": metadata,
            "capabilities": capabilities or {},
        }
        if name not in self._versions:
            self._versions[name] = []
        self._versions[name].append({"version": version, "timestamp": __import__("time").time()})

    def get(self, name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get model info.

        Args:
            name: Model name.
            version: Optional version.

        Returns:
            Optional[Dict[str, Any]]: Model info or None.
        """
        if name not in self._models:
            return None
        if version:
            return self._models[name].get(version)
        # Return latest
        versions = self._versions.get(name, [])
        if not versions:
            return None
        latest = versions[-1]
        return self._models[name].get(latest["version"])

    def list_versions(self, name: str) -> List[Dict[str, Any]]:
        """List all versions of a model.

        Args:
            name: Model name.

        Returns:
            List[Dict[str, Any]]: Version list.
        """
        return self._versions.get(name, [])

    def list_models(self) -> List[str]:
        """List all registered model names.

        Returns:
            List[str]: Model names.
        """
        return list(self._models.keys())

</final_file_content>
</write_to_file>
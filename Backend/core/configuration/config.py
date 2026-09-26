"""Configuration management for the DAIOPH system."""

import json
import os
from typing import Any, Dict, Optional


class Config:
    """Hierarchical configuration manager.

    Supports layered configuration from defaults, files, and
    environment variables with dict-style access.
    """

    def __init__(self, initial: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the config.

        Args:
            initial: Initial configuration values.
        """
        self._data: Dict[str, Any] = dict(initial or {})
        self._env_prefix = "DAIOPH_"

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Dot-notation key (e.g. "models.qwen.path").
            default: Default value if not found.

        Returns:
            Any: Configuration value.
        """
        # Check environment variable first
        env_key = f"{self._env_prefix}{key.upper().replace('.', '_')}"
        if env_key in os.environ:
            return os.environ[env_key]

        # Navigate nested dicts
        current = self._data
        for part in key.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Dot-notation key.
            value: Value to set.
        """
        parts = key.split(".")
        current = self._data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value

    def load_json(self, path: str) -> None:
        """Load configuration from a JSON file.

        Args:
            path: Path to JSON file.
        """
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self._data.update(data)

    def load_yaml(self, path: str) -> None:
        """Load configuration from a YAML file.

        Args:
            path: Path to YAML file.
        """
        try:
            import yaml

            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            self._data.update(data)
        except ImportError:
            print("[Config] PyYAML not available; skipping YAML load")

    def to_dict(self) -> Dict[str, Any]:
        """Export the full configuration.

        Returns:
            Dict[str, Any]: Configuration dict.
        """
        return dict(self._data)

    def __getattr__(self, name: str) -> Any:
        """Allow attribute-style access for top-level keys."""
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Config has no key '{name}'")
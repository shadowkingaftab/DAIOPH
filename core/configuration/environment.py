"""Environment configuration for the DAIOPH system."""

import os
from enum import Enum
from typing import Any, Dict, Optional


class Environment(Enum):
    """Supported runtime environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    EDGE = "edge"


class EnvironmentManager:
    """Resolves the active environment and its configuration."""

    ENV_VAR = "DAIOPH_ENV"

    def __init__(self) -> None:
        """Initialize the environment manager."""
        self._environment = self._detect_environment()

    def _detect_environment(self) -> Environment:
        """Detect the active environment.

        Returns:
            Environment: Detected environment.
        """
        env_name = os.getenv(self.ENV_VAR, "").lower()
        env_map = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "test": Environment.TESTING,
            "testing": Environment.TESTING,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
            "edge": Environment.EDGE,
        }
        return env_map.get(env_name, Environment.DEVELOPMENT)

    @property
    def name(self) -> str:
        """Get the environment name.

        Returns:
            str: Environment name.
        """
        return self._environment.value

    @property
    def is_production(self) -> bool:
        """Whether the environment is production.

        Returns:
            bool: True if production.
        """
        return self._environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Whether the environment is development.

        Returns:
            bool: True if development.
        """
        return self._environment == Environment.DEVELOPMENT

    @property
    def is_edge(self) -> bool:
        """Whether the environment is edge.

        Returns:
            bool: True if edge.
        """
        return self._environment == Environment.EDGE

    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get an environment variable.

        Args:
            key: Environment variable name.
            default: Default value.

        Returns:
            Optional[str]: Environment value or default.
        """
        return os.getenv(key, default)
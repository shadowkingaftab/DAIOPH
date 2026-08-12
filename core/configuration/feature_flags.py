"""Feature flag management for the DAIOPH system."""

import os
from typing import Any, Dict, Optional, Set


class FeatureFlags:
    """Manages runtime feature flags.

    Flags can be set programmatically or via environment variables
    prefixed with ``DAIOPH_FLAG_``.
    """

    ENV_PREFIX = "DAIOPH_FLAG_"

    def __init__(self, initial: Optional[Dict[str, bool]] = None) -> None:
        """Initialize the feature flags.

        Args:
            initial: Initial flag values.
        """
        self._flags: Dict[str, bool] = dict(initial or {})
        self._load_from_env()

    def _load_from_env(self) -> None:
        """Load flags from environment variables."""
        for key, value in os.environ.items():
            if key.startswith(self.ENV_PREFIX):
                flag_name = key[len(self.ENV_PREFIX):].lower()
                self._flags[flag_name] = value.lower() in ("1", "true", "yes", "on")

    def is_enabled(self, name: str, default: bool = False) -> bool:
        """Check if a feature flag is enabled.

        Args:
            name: Flag name.
            default: Default value if not set.

        Returns:
            bool: True if enabled.
        """
        return self._flags.get(name, default)

    def enable(self, name: str) -> None:
        """Enable a feature flag.

        Args:
            name: Flag name.
        """
        self._flags[name] = True

    def disable(self, name: str) -> None:
        """Disable a feature flag.

        Args:
            name: Flag name.
        """
        self._flags[name] = False

    def set(self, name: str, value: bool) -> None:
        """Set a feature flag value.

        Args:
            name: Flag name.
            value: Flag value.
        """
        self._flags[name] = value

    def all_flags(self) -> Dict[str, bool]:
        """Get all feature flags.

        Returns:
            Dict[str, bool]: Flag name to value mapping.
        """
        return dict(self._flags)

    def names(self) -> Set[str]:
        """Get all flag names.

        Returns:
            Set[str]: Flag names.
        """
        return set(self._flags.keys())
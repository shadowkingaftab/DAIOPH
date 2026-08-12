"""Configuration profiles for the DAIOPH system."""

from typing import Any, Dict, List, Optional


class ProfileManager:
    """Manages named configuration profiles.

    Profiles allow selecting predefined configuration sets
    (e.g., "lightweight", "full", "edge-only") for different
    deployment scenarios.
    """

    def __init__(self) -> None:
        """Initialize the profile manager."""
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._active_profile: Optional[str] = None

    def register(self, name: str, config: Dict[str, Any]) -> None:
        """Register a configuration profile.

        Args:
            name: Profile name.
            config: Profile configuration.
        """
        self._profiles[name] = config

    def activate(self, name: str) -> bool:
        """Activate a profile.

        Args:
            name: Profile name.

        Returns:
            bool: True if the profile was activated.
        """
        if name not in self._profiles:
            return False
        self._active_profile = name
        return True

    def get_config(self) -> Dict[str, Any]:
        """Get the active profile's configuration.

        Returns:
            Dict[str, Any]: Active profile config or empty dict.
        """
        if self._active_profile is None:
            return {}
        return dict(self._profiles.get(self._active_profile, {}))

    def list_profiles(self) -> List[str]:
        """List all registered profiles.

        Returns:
            List[str]: Profile names.
        """
        return list(self._profiles.keys())

    @property
    def active(self) -> Optional[str]:
        """Get the active profile name.

        Returns:
            Optional[str]: Active profile name.
        """
        return self._active_profile
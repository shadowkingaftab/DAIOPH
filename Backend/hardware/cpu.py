"""CPU - CPU hardware abstraction."""

from typing import Any, Dict, List, Optional


class CPU:
    """CPU hardware abstraction."""

    def __init__(self) -> None:
        """Initialize CPU abstraction."""
        self._cores = 0
        self._model = "unknown"
        self._frequency = 0.0

    def get_info(self) -> Dict[str, Any]:
        """Get CPU information.

        Returns:
            Dict[str, Any]: CPU info.
        """
        return {"cores": self._cores, "model": self._model, "frequency": self._frequency}

    def get_cores(self) -> int:
        """Get core count.

        Returns:
            int: Number of cores.
        """
        return self._cores

    def get_model(self) -> str:
        """Get CPU model.

        Returns:
            str: Model name.
        """
        return self._model



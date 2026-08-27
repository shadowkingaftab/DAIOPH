"""Secret manager (in-memory; never logs values)."""

from __future__ import annotations

import threading
from typing import Dict, Optional

__all__ = ["SecretManager"]


class SecretManager:
    """Stores secrets in memory; never logs or exposes values."""

    def __init__(self) -> None:
        self._secrets: Dict[str, str] = {}
        self._lock = threading.Lock()

    def set(self, name: str, value: str) -> None:
        """Store a secret (value never logged)."""
        with self._lock:
            self._secrets[name] = value

    def get(self, name: str) -> Optional[str]:
        """Return a secret, or None when absent."""
        with self._lock:
            return self._secrets.get(name)

    def delete(self, name: str) -> None:
        """Remove a secret (no-op when absent)."""
        with self._lock:
            self._secrets.pop(name, None)

    def names(self) -> list:
        """Return secret names (never values)."""
        with self._lock:
            return sorted(self._secrets.keys())

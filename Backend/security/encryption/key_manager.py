"""Key manager (in-memory; no persistence)."""

from __future__ import annotations

import secrets
import threading
from typing import Dict, Optional

__all__ = ["KeyManager"]


class KeyManager:
    """Generates and stores keys in memory (never persisted)."""

    def __init__(self) -> None:
        self._keys: Dict[str, bytes] = {}
        self._lock = threading.Lock()

    def generate(self, name: str, size: int = 32) -> bytes:
        """Generate and store a random key of *size* bytes."""
        key = secrets.token_bytes(size)
        with self._lock:
            self._keys[name] = key
        return key

    def get(self, name: str) -> Optional[bytes]:
        """Return the stored key, or None when absent."""
        with self._lock:
            return self._keys.get(name)

    def rotate(self, name: str, size: int = 32) -> bytes:
        """Replace and return a new key for *name*."""
        return self.generate(name, size)

    def delete(self, name: str) -> None:
        """Remove a key (no-op when absent)."""
        with self._lock:
            self._keys.pop(name, None)

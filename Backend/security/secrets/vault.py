"""Vault facade over a secret manager with rotation."""

from __future__ import annotations

import secrets
from typing import Optional

from security.secrets.secret_manager import SecretManager

__all__ = ["Vault"]


class Vault:
    """Secret storage with generation and rotation."""

    def __init__(self, manager: Optional[SecretManager] = None) -> None:
        self._manager = manager or SecretManager()

    def generate(self, name: str, length: int = 32) -> str:
        """Generate, store, and return a random secret."""
        value = secrets.token_urlsafe(length)
        self._manager.set(name, value)
        return value

    def get(self, name: str) -> Optional[str]:
        """Return a stored secret."""
        return self._manager.get(name)

    def rotate(self, name: str, length: int = 32) -> str:
        """Replace and return a new secret for *name*."""
        return self.generate(name, length)

"""Symmetric encryption (Fernet via cryptography, or honest unavailable).

Uses the well-audited ``cryptography`` Fernet construction when installed;
otherwise raises a clear error rather than inventing crypto.
"""

from __future__ import annotations

from typing import Optional

__all__ = ["EncryptionError", "Encryptor"]


class EncryptionError(RuntimeError):
    """Raised when the crypto backend is unavailable or a key is invalid."""


class Encryptor:
    """Fernet encrypt/decrypt wrapper."""

    def __init__(self, key: Optional[bytes] = None) -> None:
        try:
            from cryptography.fernet import Fernet  # type: ignore[import-not-found]
        except ImportError:
            raise EncryptionError(
                "cryptography is not installed; cannot encrypt. Install "
                "cryptography or use an injected encryptor."
            ) from None
        self._fernet = Fernet(key if key is not None else Fernet.generate_key())

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt *plaintext*."""
        return self._fernet.encrypt(plaintext)

    def decrypt(self, token: bytes) -> bytes:
        """Decrypt *token*."""
        return self._fernet.decrypt(token)

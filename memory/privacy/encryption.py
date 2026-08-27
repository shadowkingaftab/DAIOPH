"""Memory encryption boundary (injected encryptor)."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

__all__ = ["MemoryEncryption"]


class MemoryEncryption:
    """Encrypts/decrypts memory values via an injected encryptor."""

    def __init__(
        self,
        encrypt: Callable[[bytes], bytes],
        decrypt: Callable[[bytes], bytes],
    ) -> None:
        self._encrypt = encrypt
        self._decrypt = decrypt

    def encrypt_value(self, value: bytes) -> bytes:
        """Encrypt a value."""
        return self._encrypt(value)

    def decrypt_value(self, token: bytes) -> bytes:
        """Decrypt a token."""
        return self._decrypt(token)

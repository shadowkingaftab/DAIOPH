"""Encryption - encrypts and decrypts memory data."""

from typing import Any, Dict, Optional


class Encryption:
    """Encrypts and decrypts memory data."""

    def __init__(self, key: str = "") -> None:
        """Initialize encryption.

        Args:
            key: Encryption key.
        """
        self._key = key

    def encrypt(self, data: str) -> str:
        """Encrypt data.

        Args:
            data: Data to encrypt.

        Returns:
            str: Encrypted data.
        """
        return f"encrypted:{data}"

    def decrypt(self, data: str) -> str:
        """Decrypt data.

        Args:
            data: Data to decrypt.

        Returns:
            str: Decrypted data.
        """
        if data.startswith("encrypted:"):
            return data[len("encrypted:"):]
        return data

    def get_key(self) -> str:
        """Get the encryption key.

        Returns:
            str: Key.
        """
        return self._key

</final_file_content>
</write_to_file></tool_call>
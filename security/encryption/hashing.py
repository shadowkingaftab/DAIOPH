"""Password hashing (PBKDF2-HMAC-SHA256, stdlib only)."""

from __future__ import annotations

import hashlib
import hmac
import secrets

__all__ = ["hash_password", "verify_password"]


def hash_password(password: str, iterations: int = 100_000) -> str:
    """Return a salted PBKDF2 hash string ``salt$hash``."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, iterations
    )
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify *password* against a ``salt$hash`` string."""
    try:
        salt_hex, hash_hex = stored.split("$")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, 100_000
    )
    return hmac.compare_digest(digest, expected)

"""Token generation and verification (stdlib secrets/hmac)."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from typing import Optional

__all__ = ["TokenError", "TokenManager"]


class TokenError(ValueError):
    """Raised for invalid, expired, or tampered tokens."""


@dataclass(frozen=True)
class Token:
    """A signed bearer token."""

    value: str
    expires_at: float

    @property
    def expired(self) -> bool:
        """True when the token is past its expiry."""
        return time.time() > self.expires_at


class TokenManager:
    """Issues and verifies HMAC-signed tokens (no invented crypto)."""

    def __init__(self, secret: bytes, ttl_seconds: float = 3600.0) -> None:
        if not secret:
            raise ValueError("secret must be non-empty")
        self._secret = secret
        self.ttl_seconds = ttl_seconds

    def issue(self, subject: str) -> Token:
        """Issue a signed token for *subject*."""
        expires = time.time() + self.ttl_seconds
        payload = f"{subject}:{expires:.0f}".encode()
        sig = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        value = f"{payload.decode()}:{sig}"
        return Token(value=value, expires_at=expires)

    def verify(self, token: str) -> str:
        """Verify *token*; returns the subject.

        Raises:
            TokenError: On tampering, expiry, or malformed tokens.
        """
        parts = token.split(":")
        if len(parts) != 3:
            raise TokenError("malformed token")
        subject, expires_str, sig = parts
        try:
            expires = float(expires_str)
        except ValueError:
            raise TokenError("malformed expiry") from None
        payload = f"{subject}:{expires:.0f}".encode()
        expected = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise TokenError("token signature mismatch")
        if time.time() > expires:
            raise TokenError("token expired")
        return subject

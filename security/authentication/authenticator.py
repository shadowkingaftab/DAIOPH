"""Authenticator with injectable credential verifier."""

from __future__ import annotations

from typing import Callable, Optional

from security.authentication.session import Session, SessionManager
from security.authentication.tokens import Token, TokenManager

__all__ = ["Authenticator", "AuthenticationError"]

Verifier = Callable[[str, str], bool]


class AuthenticationError(PermissionError):
    """Raised when credentials are rejected."""


class Authenticator:
    """Authenticates credentials via an injected verifier (deny by default)."""

    def __init__(
        self,
        verifier: Optional[Verifier] = None,
        sessions: Optional[SessionManager] = None,
        tokens: Optional[TokenManager] = None,
    ) -> None:
        self._verifier = verifier
        self.sessions = sessions or SessionManager()
        self.tokens = tokens

    def authenticate(self, username: str, password: str) -> Session:
        """Verify credentials and open a session.

        Raises:
            AuthenticationError: When no verifier is wired or credentials
                are rejected.
        """
        if self._verifier is None:
            raise AuthenticationError(
                "no credential verifier injected; cannot authenticate"
            )
        if not self._verifier(username, password):
            raise AuthenticationError("invalid credentials")
        return self.sessions.create(username)

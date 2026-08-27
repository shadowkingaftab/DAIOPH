"""Authorizer facade over a policy."""

from __future__ import annotations

from security.authorization.policies import Policy, PolicyError

__all__ = ["Authorizer"]


class Authorizer:
    """Wraps a :class:`Policy` with a deny-by-default check."""

    def __init__(self, policy: Policy) -> None:
        self.policy = policy

    def authorize(self, subject: str, permission: str) -> bool:
        """True when permitted; never raises."""
        return self.policy.check(subject, permission)

    def require(self, subject: str, permission: str) -> None:
        """Raise :class:`PolicyError` when not permitted."""
        self.policy.require(subject, permission)

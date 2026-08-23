"""Dependency injection container for REST route handlers.

:class:`DependencyContainer` is a small service locator: providers are
registered as factories or singletons and resolved lazily on first use.
Route modules receive the container and pull their collaborators from it,
keeping handlers testable (swap fakes in tests) and decoupled from
construction details.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

__all__ = ["DependencyContainer", "DependencyMissingError", "RequestContext"]


class DependencyMissingError(KeyError):
    """Raised when resolving a name that was never registered."""


@dataclass
class RequestContext:
    """Per-request context handed to route handlers."""

    correlation_id: str
    container: "DependencyContainer"
    attributes: Dict[str, Any] = field(default_factory=dict)


class DependencyContainer:
    """Thread-safe lazy dependency registry."""

    def __init__(self) -> None:
        self._providers: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, bool] = {}
        self._cache: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        provider: Callable[[], Any],
        singleton: bool = True,
    ) -> None:
        """Register *provider* under *name*.

        Args:
            name: Resolution key.
            provider: Zero-argument callable producing the dependency.
            singleton: Cache the first resolution for later lookups.
        """
        with self._lock:
            self._providers[name] = provider
            self._singletons[name] = singleton
            self._cache.pop(name, None)

    def register_value(self, name: str, value: Any) -> None:
        """Register an already-constructed *value* (always singleton)."""
        self.register(name, lambda: value, singleton=True)

    def resolve(self, name: str) -> Any:
        """Produce the dependency registered under *name*.

        Raises:
            DependencyMissingError: If *name* was never registered.
        """
        with self._lock:
            if name in self._cache:
                return self._cache[name]
            provider = self._providers.get(name)
            if provider is None:
                raise DependencyMissingError(name)
            value = provider()
            if self._singletons.get(name, True):
                self._cache[name] = value
            return value

    def try_resolve(self, name: str, default: Any = None) -> Any:
        """Like :meth:`resolve` but returns *default* when unregistered."""
        try:
            return self.resolve(name)
        except DependencyMissingError:
            return default

    def override(self, name: str, value: Any) -> None:
        """Force *value* for *name* (used by tests to inject fakes)."""
        with self._lock:
            self._cache[name] = value
            self._providers.setdefault(name, lambda: value)
            self._singletons[name] = True

    def names(self) -> list:
        """All registered dependency names."""
        with self._lock:
            return sorted(self._providers.keys())

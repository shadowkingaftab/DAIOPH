from __future__ import annotations


class SystemManager:
    """Manages system-level operations."""

    def __init__(self) -> None:
        self.services: dict[str, bool] = {}

    def start_service(self, name: str) -> None:
        """Start a system service."""
        self.services[name] = True
        print(f"Service '{name}' started")

    def stop_service(self, name: str) -> None:
        """Stop a system service."""
        self.services[name] = False
        print(f"Service '{name}' stopped")

    def is_service_running(self, name: str) -> bool:
        """Check if a service is running."""
        return self.services.get(name, False)
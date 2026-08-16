from __future__ import annotations

from typing import Any, Dict, List


class PoisoningDetector:
    """Detects malicious or anomalous client updates."""

    def __init__(self, threshold: float = 2.0) -> None:
        self.threshold = threshold
        self.suspicious_clients: List[str] = []

    def detect(self, update: Dict[str, Any], baseline: Dict[str, Any]) -> bool:
        """Check if an update deviates significantly from a baseline.

        Returns:
            True if the update is suspicious, False otherwise.
        """
        deviation = 0.0
        count = 0
        for key, value in update.items():
            if key in baseline and isinstance(value, (int, float)):
                base = baseline[key]
                if isinstance(base, (int, float)) and abs(base) > 1e-9:
                    deviation += abs(value - base) / abs(base)
                    count += 1
        if count == 0:
            return False
        mean_deviation = deviation / count
        return mean_deviation > self.threshold

    def flag_client(self, client_id: str) -> None:
        """Flag a client as suspicious."""
        if client_id not in self.suspicious_clients:
            self.suspicious_clients.append(client_id)

    def is_suspicious(self, client_id: str) -> bool:
        """Check if a client is flagged as suspicious."""
        return client_id in self.suspicious_clients

    def get_suspicious(self) -> List[str]:
        """Return the list of suspicious clients."""
        return list(self.suspicious_clients)
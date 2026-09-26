from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class MonitorAgent:
    """Monitors system resources, task execution, and agent health."""

    def __init__(self, name: str = "monitor") -> None:
        self.name = name
        self.metrics: Dict[str, Any] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.running: bool = False
        self.start_time: Optional[float] = None

    def start(self) -> None:
        """Start the monitoring loop."""
        self.running = True
        self.start_time = time.time()

    def stop(self) -> None:
        """Stop the monitoring loop."""
        self.running = False

    def record_metric(self, key: str, value: Any) -> None:
        """Record a metric value."""
        self.metrics[key] = value

    def get_metric(self, key: str) -> Any:
        """Retrieve a recorded metric value."""
        return self.metrics.get(key)

    def check_health(self) -> Dict[str, Any]:
        """Check the health of the monitored system."""
        uptime = 0.0
        if self.start_time is not None:
            uptime = time.time() - self.start_time
        return {
            "status": "healthy" if self.running else "stopped",
            "uptime": uptime,
            "metrics_count": len(self.metrics),
            "alerts_count": len(self.alerts),
        }

    def raise_alert(self, level: str, message: str) -> None:
        """Raise an alert with the given level and message."""
        self.alerts.append(
            {
                "level": level,
                "message": message,
                "timestamp": time.time(),
            }
        )

    def get_alerts(self, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve alerts, optionally filtered by level."""
        if level is None:
            return list(self.alerts)
        return [a for a in self.alerts if a["level"] == level]

    def clear_alerts(self) -> None:
        """Clear all recorded alerts."""
        self.alerts.clear()

    def snapshot(self) -> Dict[str, Any]:
        """Return a snapshot of the current monitoring state."""
        return {
            "name": self.name,
            "running": self.running,
            "metrics": dict(self.metrics),
            "alerts": list(self.alerts),
            "health": self.check_health(),
        }
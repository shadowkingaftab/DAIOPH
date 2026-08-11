"""Session management for the DAIOPH Streamlit app.

Handles user session tracking, execution history, and telemetry.
"""

import time
import uuid
from typing import Any, Dict, List, Optional


class SessionManager:
    """Manages a Streamlit user session."""

    def __init__(self) -> None:
        """Initialize the session manager."""
        self.session_id = str(uuid.uuid4())
        self.started_at = time.time()
        self.execution_count = 0
        self.total_latency = 0.0
        self.route_counts: Dict[str, int] = {}
        self.history: List[Dict[str, Any]] = []

    def record_execution(
        self,
        prompt: str,
        route: str,
        latency: float,
        status: str = "success",
        output: str = "",
    ) -> Dict[str, Any]:
        """Record a single execution.

        Args:
            prompt: The user prompt.
            route: Route used (ODA/Hybrid/Cloud).
            latency: Execution latency in seconds.
            status: Execution status.
            output: Final output.

        Returns:
            Dict[str, Any]: The recorded execution record.
        """
        self.execution_count += 1
        self.total_latency += latency
        self.route_counts[route] = self.route_counts.get(route, 0) + 1

        record = {
            "id": f"exec_{self.execution_count}",
            "timestamp": time.time(),
            "prompt": prompt,
            "route": route,
            "latency": latency,
            "status": status,
            "output": output,
        }
        self.history.append(record)
        return record

    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated session metrics.

        Returns:
            Dict[str, Any]: Session metrics.
        """
        avg_latency = (
            self.total_latency / self.execution_count if self.execution_count else 0
        )
        return {
            "session_id": self.session_id,
            "executions": self.execution_count,
            "avg_latency": avg_latency,
            "total_latency": self.total_latency,
            "route_counts": self.route_counts,
            "uptime": time.time() - self.started_at,
        }

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get execution history.

        Args:
            limit: Optional number of records to return (most recent).

        Returns:
            List[Dict[str, Any]]: Execution history.
        """
        if limit:
            return self.history[-limit:]
        return self.history
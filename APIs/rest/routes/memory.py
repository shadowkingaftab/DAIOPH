from __future__ import annotations

from typing import Any, Dict, List


class MemoryRoute:
    """Memory-related REST routes."""

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {"total_entries": 0, "active_sessions": 0}

    def get_recent_entries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent memory entries."""
        return []

    def clear_memory(self) -> Dict[str, Any]:
        """Clear memory state."""
        return {"status": "cleared"}
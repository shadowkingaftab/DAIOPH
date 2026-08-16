from __future__ import annotations

from typing import Any, Dict, List


class ChatRoute:
    """Chat-related REST routes."""

    def get_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent messages."""
        return []

    def send_message(self, content: str, sender: str) -> Dict[str, Any]:
        """Send a new message."""
        return {"status": "sent", "message_id": ""}

    def get_history(self, peer_id: str) -> List[Dict[str, Any]]:
        """Get message history for a peer."""
        return []
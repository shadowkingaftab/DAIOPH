from __future__ import annotations

from typing import Any, Dict, List


class Tracer:
    """Tracing utility for request tracking."""

    def __init__(self) -> None:
        self.spans: List[Dict[str, Any]] = []

    def start_span(self, name: str, attributes: Dict[str, Any] = {}) -> str:
        """Start a new trace span."""
        span_id = f"span_{len(self.spans)}"
        self.spans.append({
            "id": span_id,
            "name": name,
            "attributes": attributes,
            "started": True,
        })
        return span_id

    def end_span(self, span_id: str) -> None:
        """End a trace span."""
        for span in self.spans:
            if span["id"] == span_id:
                span["started"] = False
                break

    def get_spans(self) -> List[Dict[str, Any]]:
        """Return all recorded spans."""
        return list(self.spans)
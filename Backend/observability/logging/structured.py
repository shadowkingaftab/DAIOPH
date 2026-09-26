from __future__ import annotations

from typing import Any, Dict


class StructuredLogger:
    """Structured logging utility."""

    def __init__(self, name: str = "DAIOPH") -> None:
        self.name = name

    def log(self, level: str, message: str, **kwargs: Any) -> None:
        """Log a structured message."""
        entry = {"level": level, "message": message, "logger": self.name}
        entry.update(kwargs)
        self._output(entry)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self.log("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self.log("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        self.log("error", message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self.log("debug", message, **kwargs)

    def _output(self, entry: Dict[str, Any]) -> None:
        """Output a log entry."""
        import json
        print(json.dumps(entry))
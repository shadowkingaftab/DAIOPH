"""Perception - processes raw sensory input into structured representations."""

from typing import Any, Dict, List, Optional


class Perception:
    """Transforms raw sensory data into meaningful perceptions."""

    def process(self, raw_input: Any, sensor_type: str = "general") -> Dict[str, Any]:
        """Process raw input into a perception.

        Args:
            raw_input: Raw sensory data.
            sensor_type: Type of sensor (visual, auditory, etc.).

        Returns:
            Dict[str, Any]: Processed perception.
        """
        perception = {
            "type": sensor_type,
            "timestamp": __import__("time").time(),
            "raw": raw_input,
            "features": self._extract_features(raw_input),
        }
        return perception

    def _extract_features(self, data: Any) -> Dict[str, Any]:
        """Extract features from raw data.

        Args:
            data: Input data.

        Returns:
            Dict[str, Any]: Extracted features.
        """
        if isinstance(data, str):
            return {"length": len(data), "has_numbers": any(c.isdigit() for c in data)}
        if isinstance(data, dict):
            return {k: type(v).__name__ for k, v in data.items()}
        return {"type": type(data).__name__}

    def reset(self) -> None:
        """Reset the perception module."""
        pass

</final_file_content>
</write_to_file>
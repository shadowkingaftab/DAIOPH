"""SensorProcessor - processes sensor input."""

from typing import Any, Dict, List, Optional


class SensorProcessor:
    """Processes sensor input for multimodal pipeline."""

    def __init__(self) -> None:
        """Initialize the sensor processor."""
        self._sensor_types = ["accelerometer", "gyroscope", "magnetometer", "gps"]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process sensor input.

        Args:
            input_data: Input data dict.

        Returns:
            Dict[str, Any]: Processed result.
        """
        sensor_data = input_data.get("sensor_data", {})
        return {"sensor_data": sensor_data, "types": self._sensor_types, "processed": True}

    def get_sensor_types(self) -> List[str]:
        """Get supported sensor types.

        Returns:
            List[str]: Sensor types.
        """
        return list(self._sensor_types)

</final_file_content>
</write_to_file></tool_call>
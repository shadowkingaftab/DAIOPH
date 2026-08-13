"""SensorManager - manages sensor data collection."""

from typing import Any, Dict, List, Optional


class SensorManager:
    """Manages sensor data collection and processing."""

    def __init__(self) -> None:
        """Initialize the sensor manager."""
        self._sensors: Dict[str, Any] = {}

    def register(self, name: str, sensor: Any) -> None:
        """Register a sensor.

        Args:
            name: Sensor name.
            sensor: Sensor instance.
        """
        self._sensors[name] = sensor

    def read(self, name: str) -> Any:
        """Read from a sensor.

        Args:
            name: Sensor name.

        Returns:
            Any: Sensor data.
        """
        sensor = self._sensors.get(name)
        if sensor:
            return sensor.read()
        return None

    def list_sensors(self) -> List[str]:
        """List all sensors.

        Returns:
            List[str]: Sensor names.
        """
        return list(self._sensors.keys())

</final_file_content>
</write_to_file></tool_call>
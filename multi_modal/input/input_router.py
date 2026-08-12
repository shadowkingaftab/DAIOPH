"""InputRouter - routes multimodal inputs."""

from typing import Any, Dict, List, Optional


class InputRouter:
    """Routes multimodal inputs to appropriate processors."""

    def __init__(self) -> None:
        """Initialize the input router."""
        self._routes: Dict[str, str] = {}
        self._processors: Dict[str, Any] = {}

    def add_route(self, modality: str, processor: str) -> None:
        """Add a routing rule.

        Args:
            modality: Modality type.
            processor: Processor name.
        """
        self._routes[modality] = processor

    def route(self, input_data: Dict[str, Any]) -> Any:
        """Route input to appropriate processor.

        Args:
            input_data: Input data dict.

        Returns:
            Any: Processed result.
        """
        modality = input_data.get("modality", "")
        processor_name = self._routes.get(modality)
        if processor_name and processor_name in self._processors:
            return self._processors[processor_name].process(input_data)
        return None

    def register_processor(self, name: str, processor: Any) -> None:
        """Register a processor.

        Args:
            name: Processor name.
            processor: Processor instance.
        """
        self._processors[name] = processor

</final_file_content>
</write_to_file></tool_call>
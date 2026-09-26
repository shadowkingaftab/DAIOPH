"""WhisperLocalProvider - local Whisper model provider."""

from typing import Any, Dict, Optional


class WhisperLocalProvider:
    """Provides local Whisper model loading and execution."""

    def __init__(self, model_path: str = "") -> None:
        """Initialize the Whisper local provider.

        Args:
            model_path: Path to model file.
        """
        self._model_path = model_path

    def load(self, **kwargs: Any) -> Any:
        """Load the Whisper model.

        Args:
            **kwargs: Additional loading arguments.

        Returns:
            Any: Loaded model instance.
        """
        return {"model": "whisper", "path": self._model_path, "loaded": True}

    def execute(self, input_data: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the model.

        Args:
            input_data: Input data.
            **kwargs: Additional execution arguments.

        Returns:
            Dict[str, Any]: Execution result.
        """
        return {"output": "whisper_response", "model": "whisper"}

</final_file_content>
</write_to_file></tool_call>
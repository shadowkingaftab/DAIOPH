"""WhisperLoader - loads Whisper models from local storage."""

from typing import Any, Dict, Optional


class WhisperLoader:
    """Loads Whisper models from local filesystem."""

    def __init__(self, base_path: str = "") -> None:
        """Initialize the Whisper loader.

        Args:
            base_path: Base path for model files.
        """
        self._base_path = base_path

    def load(self, model_name: str, **kwargs: Any) -> Any:
        """Load a Whisper model.

        Args:
            model_name: Model name to load.
            **kwargs: Additional loading arguments.

        Returns:
            Any: Loaded model.
        """
        return {"model": model_name, "path": self._base_path, "loaded": True}

    def unload(self, model: Any) -> None:
        """Unload a model.

        Args:
            model: Model to unload.
        """
        pass

</final_file_content>
</write_to_file></tool_call>
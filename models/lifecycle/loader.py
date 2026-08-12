"""ModelLoader - loads models into memory."""

from typing import Any, Dict, Optional


class ModelLoader:
    """Loads models into memory for execution."""

    def __init__(self) -> None:
        """Initialize the model loader."""
        self._loaded_models: Dict[str, Any] = {}

    def load(self, model_path: str, model_name: str) -> Any:
        """Load a model from path.

        Args:
            model_path: Path to model file.
            model_name: Name to register the model under.

        Returns:
            Any: Loaded model.
        """
        model = {"path": model_path, "loaded": True}
        self._loaded_models[model_name] = model
        return model

    def get(self, model_name: str) -> Optional[Any]:
        """Get a loaded model.

        Args:
            model_name: Model name.

        Returns:
            Optional[Any]: Loaded model or None.
        """
        return self._loaded_models.get(model_name)

    def unload(self, model_name: str) -> None:
        """Unload a model.

        Args:
            model_name: Model name to unload.
        """
        self._loaded_models.pop(model_name, None)

</final_file_content>
</write_to_file></tool_call>
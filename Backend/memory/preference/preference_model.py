"""PreferenceModel - models user preferences."""

from typing import Any, Dict, Optional


class PreferenceModel:
    """Models user preferences for prediction."""

    def __init__(self) -> None:
        """Initialize the preference model."""
        self._weights: Dict[str, float] = {}

    def set_weight(self, key: str, weight: float) -> None:
        """Set a preference weight.

        Args:
            key: Preference key.
            weight: Weight value.
        """
        self._weights[key] = weight

    def get_weight(self, key: str, default: float = 0.5) -> float:
        """Get a preference weight.

        Args:
            key: Preference key.
            default: Default weight.

        Returns:
            float: Weight value.
        """
        return self._weights.get(key, default)

    def predict(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Predict preferences for a context.

        Args:
            context: Context dict.

        Returns:
            Dict[str, float]: Predicted preferences.
        """
        return dict(self._weights)

</final_file_content>
</write_to_file></tool_call>
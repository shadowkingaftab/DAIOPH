"""ModalityFusion - fuses data from multiple modalities."""

from typing import Any, Dict, List, Optional


class ModalityFusion:
    """Fuses data from multiple modalities."""

    def __init__(self) -> None:
        """Initialize modality fusion."""
        self._modalities: Dict[str, Any] = {}

    def add_modality(self, name: str, data: Any) -> None:
        """Add modality data.

        Args:
            name: Modality name.
            data: Modality data.
        """
        self._modalities[name] = data

    def fuse(self) -> Dict[str, Any]:
        """Fuse all modalities.

        Returns:
            Dict[str, Any]: Fused result.
        """
        return {"fused": True, "modalities": list(self._modalities.keys())}

    def get_modalities(self) -> List[str]:
        """Get all modality names.

        Returns:
            List[str]: Modality names.
        """
        return list(self._modalities.keys())

</final_file_content>
</write_to_file></tool_call>
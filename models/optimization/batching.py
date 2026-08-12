"""Batching - model batching optimization."""

from typing import Any, Dict, List, Optional


class Batching:
    """Applies batching optimization to models."""

    def __init__(self, batch_size: int = 32) -> None:
        """Initialize batching.

        Args:
            batch_size: Batch size for inference.
        """
        self._batch_size = batch_size

    def batch(self, inputs: List[Any]) -> List[List[Any]]:
        """Split inputs into batches.

        Args:
            inputs: List of input items.

        Returns:
            List[List[Any]]: Batched inputs.
        """
        return [inputs[i:i + self._batch_size] for i in range(0, len(inputs), self._batch_size)]

    def get_batch_size(self) -> int:
        """Get batch size.

        Returns:
            int: Batch size.
        """
        return self._batch_size

</final_file_content>
</write_to_file></tool_call>
"""EmbeddingStore - stores embeddings for retrieval."""

from typing import Any, Dict, List, Optional


class EmbeddingStore:
    """Stores embeddings for retrieval."""

    def __init__(self) -> None:
        """Initialize the embedding store."""
        self._embeddings: Dict[str, List[float]] = {}

    def store(self, key: str, embedding: List[float]) -> None:
        """Store an embedding.

        Args:
            key: Embedding key.
            embedding: Embedding vector.
        """
        self._embeddings[key] = embedding

    def retrieve(self, key: str) -> Optional[List[float]]:
        """Retrieve an embedding.

        Args:
            key: Embedding key.

        Returns:
            Optional[List[float]]: Embedding or None.
        """
        return self._embeddings.get(key)

    def list_keys(self) -> List[str]:
        """List all embedding keys.

        Returns:
            List[str]: All keys.
        """
        return list(self._embeddings.keys())

</final_file_content>
</write_to_file></tool_call>
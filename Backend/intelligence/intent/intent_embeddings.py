"""Intent embeddings - vector-based intent representation."""

from typing import Any, Dict, List, Optional
import hashlib


class IntentEmbeddings:
    """Vector-based representation of intents for similarity matching."""

    def __init__(self, dimension: int = 64) -> None:
        """Initialize the intent embeddings.

        Args:
            dimension: Embedding dimension size.
        """
        self._dimension = dimension
        self._embeddings: Dict[str, List[float]] = {}

    def encode(self, intent_name: str) -> List[float]:
        """Encode an intent name into a vector.

        Args:
            intent_name: Name of the intent.

        Returns:
            List[float]: Intent embedding vector.
        """
        # Deterministic hash-based embedding
        hash_obj = hashlib.sha256(intent_name.encode()).hexdigest()
        seed = int(hash_obj[:8], 16)
        rng = __import__("random").Random(seed)
        embedding = [rng.random() for _ in range(self._dimension)]
        # Normalize roughly
        length = sum(x * x for x in embedding) ** 0.5
        if length > 0:
            embedding = [x / length for x in embedding]
        self._embeddings[intent_name] = embedding
        return embedding

    def similarity(self, a: str, b: str) -> float:
        """Compute cosine similarity between two intent embeddings.

        Args:
            a: First intent name.
            b: Second intent name.

        Returns:
            float: Cosine similarity in [-1, 1].
        """
        vec_a = self.encode(a)
        vec_b = self.encode(b)
        dot = sum(x * y for x, y in zip(vec_a, vec_b))
        mag_a = sum(x * x for x in vec_a) ** 0.5
        mag_b = sum(x * x for x in vec_b) ** 0.5
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def get(self, intent_name: str) -> Optional[List[float]]:
        """Get an existing embedding.

        Args:
            intent_name: Intent name.

        Returns:
            Optional[List[float]]: Embedding vector or None.
        """
        return self._embeddings.get(intent_name)
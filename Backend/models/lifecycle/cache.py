"""ModelCache - caches loaded models."""

from typing import Any, Dict, Optional


class ModelCache:
    """Caches loaded models for reuse."""

    def __init__(self, max_size: int = 10) -> None:
        """Initialize the model cache.

        Args:
            max_size: Maximum number of cached models.
        """
        self._max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._access_order: List[str] = []

    def put(self, key: str, model: Any) -> None:
        """Cache a model.

        Args:
            key: Cache key.
            model: Model to cache.
        """
        if key in self._cache:
            self._access_order.remove(key)
        elif len(self._cache) >= self._max_size:
            oldest = self._access_order.pop(0)
            del self._cache[oldest]
        self._cache[key] = model
        self._access_order.append(key)

    def get(self, key: str) -> Optional[Any]:
        """Get a cached model.

        Args:
            key: Cache key.

        Returns:
            Optional[Any]: Cached model or None.
        """
        return self._cache.get(key)

    def evict(self, key: str) -> None:
        """Evict a model from cache.

        Args:
            key: Cache key.
        """
        self._cache.pop(key, None)
        if key in self._access_order:
            self._access_order.remove(key)

    def clear(self) -> None:
        """Clear the cache."""
        self._cache = {}
        self._access_order = []

</final_file_content>
</write_to_file></tool_call>
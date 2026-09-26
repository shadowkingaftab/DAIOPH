from __future__ import annotations

from typing import Any, Dict, List


class DistributedMemory:
    """Distributed shared memory across network nodes."""

    def __init__(self) -> None:
        self.shards: Dict[str, Dict[str, Any]] = {}

    def create_shard(self, shard_id: str) -> None:
        """Create a new memory shard."""
        self.shards[shard_id] = {}

    def put(self, shard_id: str, key: str, value: Any) -> bool:
        """Put a value into a distributed shard."""
        if shard_id not in self.shards:
            return False
        self.shards[shard_id][key] = value
        return True

    def get(self, shard_id: str, key: str) -> Any:
        """Get a value from a distributed shard."""
        shard = self.shards.get(shard_id, {})
        return shard.get(key)

    def get_shard(self, shard_id: str) -> Dict[str, Any]:
        """Return the full contents of a shard."""
        return dict(self.shards.get(shard_id, {}))

    def get_shard_ids(self) -> List[str]:
        """Return all shard IDs."""
        return list(self.shards.keys())
"""ReplayBuffer - stores experience for continual learning."""

from typing import Any, Dict, List, Optional


class ReplayBuffer:
    """Stores experience replays for continual learning."""

    def __init__(self, capacity: int = 1000) -> None:
        """Initialize the replay buffer.

        Args:
            capacity: Maximum number of experiences.
        """
        self._capacity = capacity
        self._storage: List[Any] = []
        self._position = 0

    def store(self, experience: Any) -> None:
        """Store an experience.

        Args:
            experience: Experience to store.
        """
        if len(self._storage) < self._capacity:
            self._storage.append(experience)
        else:
            self._storage[self._position] = experience
            self._position = (self._position + 1) % self._capacity

    def sample(self, batch_size: int) -> List[Any]:
        """Sample a batch of experiences.

        Args:
            batch_size: Number of experiences to sample.

        Returns:
            List[Any]: Sampled batch.
        """
        batch_size = min(batch_size, len(self._storage))
        import random
        return random.sample(self._storage, batch_size)

    def __len__(self) -> int:
        """Get the number of stored experiences.

        Returns:
            int: Count of experiences.
        """
        return len(self._storage)

    def reset(self) -> None:
        """Reset the buffer."""
        self._storage = []
        self._position = 0

</final_file_content>
</write_to_file>
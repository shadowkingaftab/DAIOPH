"""Deterministic dataset construction and splitting."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence, Tuple

__all__ = ["DatasetBuilder", "Example"]


@dataclass(frozen=True)
class Example:
    """A labeled training example."""

    text: str
    label: str


class DatasetBuilder:
    """Collects examples and produces deterministic train/val splits."""

    def __init__(self, seed: int = 0) -> None:
        self._examples: List[Example] = []
        self._seed = seed

    def add(self, text: str, label: str) -> Example:
        """Add a labeled example."""
        example = Example(text=text, label=label)
        self._examples.append(example)
        return example

    def __len__(self) -> int:
        return len(self._examples)

    def examples(self) -> List[Example]:
        """All examples in insertion order."""
        return list(self._examples)

    def labels(self) -> List[str]:
        """Distinct labels in first-seen order."""
        seen: List[str] = []
        for ex in self._examples:
            if ex.label not in seen:
                seen.append(ex.label)
        return seen

    def split(
        self, validation_ratio: float = 0.2
    ) -> Tuple[List[Example], List[Example]]:
        """Shuffled (seeded) train/validation split.

        The shuffle uses a local Random(self._seed) so repeated calls with
        the same data return identical splits regardless of global state.
        """
        if not 0.0 <= validation_ratio < 1.0:
            raise ValueError("validation_ratio must be within [0, 1)")
        examples = list(self._examples)
        rng = random.Random(self._seed)
        rng.shuffle(examples)
        n_val = int(len(examples) * validation_ratio)
        return examples[n_val:], examples[:n_val]

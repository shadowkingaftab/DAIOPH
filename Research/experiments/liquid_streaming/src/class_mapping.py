"""Stable class-to-output-row mapping for incremental output heads."""
from __future__ import annotations

from typing import Dict, Iterable, List


def append_new_classes(classes_seen: List[str], label_to_idx: Dict[str, int],
                       incoming_labels: Iterable[str]) -> Dict[str, int]:
    """Append newly observed labels without changing any existing row index."""
    for label in sorted(set(incoming_labels)):
        if label not in label_to_idx:
            label_to_idx[label] = len(classes_seen)
            classes_seen.append(label)
    if len(classes_seen) != len(label_to_idx):
        raise ValueError("classes_seen and label_to_idx are inconsistent")
    if any(label_to_idx[label] != index for index, label in enumerate(classes_seen)):
        raise ValueError("class indices must match append-only output-head rows")
    return dict(label_to_idx)

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple


def create_class_incremental_chunks(train_list: List[Tuple[str, str]], num_chunks: int = 5, seed: int = 12345):
    """Create 5 deterministic class-incremental chunks. Test utterances never enter training."""
    rng = random.Random(seed)
    # get all labels in train
    labels = sorted(list(set(l for _, l in train_list)))
    # deterministic order
    rng.shuffle(labels)
    intent_order = labels
    # split labels across chunks roughly equally
    chunk_size = len(intent_order) // num_chunks
    chunks = []
    for i in range(num_chunks):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_chunks - 1 else len(intent_order)
        chunk_labels = set(intent_order[start:end])
        # collect training examples for this chunk (only train_list)
        train_ex = [(t, l) for t, l in train_list if l in chunk_labels]
        # shuffle deterministically
        rng.shuffle(train_ex)
        chunks.append({
            "chunk_id": i,
            "labels": sorted(list(chunk_labels)),
            "train": train_ex,
        })
    return chunks, intent_order

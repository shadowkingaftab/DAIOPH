from __future__ import annotations

import os
from typing import List, Tuple

import torch
import torch.nn as nn
from ncps.torch import CfC


class CfcTextClassifier(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_size: int = 64, num_classes: int = 10, pad_id: int = 0):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_id)
        # Use official CfC API
        self.cfc = CfC(input_size=embed_dim, units=hidden_size, return_sequences=False, batch_first=True)
        self.head = nn.Linear(hidden_size, num_classes)
        self.pad_id = pad_id

    def forward(self, input_ids, lengths=None):
        # input_ids: (B, T)
        emb = self.embedding(input_ids)
        # CfC expects (B, T, input_size) if batch_first=True
        out, _ = self.cfc(emb)
        # out shape depends on return_sequences=False -> last state
        if isinstance(out, (list, tuple)):
            out = out[0]
        # if still has time dim, take last
        if out.dim() == 3:
            out = out[:, -1, :]
        logits = self.head(out)
        return logits

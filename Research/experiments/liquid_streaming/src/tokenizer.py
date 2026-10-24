from __future__ import annotations

import re
from collections import Counter
from typing import Dict, Iterable, List


class SimpleTokenizer:
    """Tokenizer built from training text only."""

    def __init__(self, texts: Iterable[str], min_freq: int = 1, max_vocab_size: int = 20000):
        self.pad_token = "<pad>"
        self.unk_token = "<unk>"
        self.specials = [self.pad_token, self.unk_token]
        counter = Counter()
        for t in texts:
            for tok in self._tokenize(t):
                counter[tok] += 1
        vocab_tokens = []
        for tok, freq in counter.most_common(max_vocab_size):
            if freq < min_freq:
                continue
            if tok in self.specials:
                continue
            vocab_tokens.append(tok)
        self.itos = self.specials + vocab_tokens
        self.stoi: Dict[str, int] = {s: i for i, s in enumerate(self.itos)}
        self.pad_id = self.stoi[self.pad_token]
        self.unk_id = self.stoi[self.unk_token]
        self.vocab_size = len(self.itos)

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = re.findall(r"[a-z0-9']+", text)
        if not tokens:
            tokens = text.split()
        return tokens

    def encode(self, text: str, max_len: int = 64) -> List[int]:
        ids = []
        for tok in self._tokenize(text):
            ids.append(self.stoi.get(tok, self.unk_id))
            if len(ids) >= max_len:
                break
        if len(ids) == 0:
            ids = [self.unk_id]
        return ids

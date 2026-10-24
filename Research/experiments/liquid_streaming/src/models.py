"""Model wrappers for the liquid streaming study.

Patterns follow the existing ``src/model_cfc.py`` (``CfcTextClassifier``):
Embedding -> recurrent layer -> linear classification head.

The recurrent models support a growing classification head so that, as new
intent chunks arrive, previously learned class weights are preserved while new
class logits are added (class-incremental setting).
"""
from __future__ import annotations

import torch
import torch.nn as nn
from ncps.torch import CfC

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
import numpy as np


def expand_linear(head: nn.Linear, new_out_features: int) -> nn.Linear:
    """Return a new Linear that preserves the old weights for existing classes."""
    old_out, in_features = head.weight.shape
    if new_out_features <= old_out:
        return head
    new_head = nn.Linear(in_features, new_out_features)
    with torch.no_grad():
        new_head.weight[:old_out] = head.weight
        new_head.bias[:old_out] = head.bias
        # new rows: small random init (zeros bias)
        nn.init.xavier_uniform_(new_head.weight[old_out:])
        new_head.bias[old_out:].zero_()
    return new_head


class BaseTextClassifier(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_size: int = 64,
                 num_classes: int = 10, pad_id: int = 0):
        super().__init__()
        self.embed_dim = embed_dim
        self.hidden_size = hidden_size
        self.pad_id = pad_id
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_id)
        self.head = nn.Linear(hidden_size, num_classes)
        self.num_classes = num_classes

    def set_num_classes(self, new_num_classes: int):
        if new_num_classes <= self.num_classes:
            return
        self.head = expand_linear(self.head, new_num_classes)
        self.num_classes = new_num_classes

    def forward(self, input_ids, lengths=None):
        raise NotImplementedError


class CfcTextClassifier(BaseTextClassifier):
    """Official ncps CfC liquid-time-constant text classifier."""

    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_size: int = 64,
                 num_classes: int = 10, pad_id: int = 0):
        super().__init__(vocab_size, embed_dim, hidden_size, num_classes, pad_id)
        self.cfc = CfC(input_size=embed_dim, units=hidden_size,
                       return_sequences=False, batch_first=True)

    def forward(self, input_ids, lengths=None):
        emb = self.embedding(input_ids)                     # (B, T, E)
        out, _ = self.cfc(emb)                              # (B, H) because return_sequences=False
        if isinstance(out, (list, tuple)):
            out = out[0]
        if out.dim() == 3:
            out = out[:, -1, :]
        return self.head(out)


class LSTMTextClassifier(BaseTextClassifier):
    """Standard LSTM text classifier (baseline)."""

    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_size: int = 64,
                 num_classes: int = 10, pad_id: int = 0):
        super().__init__(vocab_size, embed_dim, hidden_size, num_classes, pad_id)
        self.rnn = nn.LSTM(embed_dim, hidden_size, batch_first=True)

    def forward(self, input_ids, lengths=None):
        emb = self.embedding(input_ids)                     # (B, T, E)
        _, (h, _) = self.rnn(emb)                           # h: (num_layers, B, H)
        return self.head(h[-1])


class GRUTextClassifier(BaseTextClassifier):
    """Standard GRU text classifier (baseline)."""

    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_size: int = 64,
                 num_classes: int = 10, pad_id: int = 0):
        super().__init__(vocab_size, embed_dim, hidden_size, num_classes, pad_id)
        self.rnn = nn.GRU(embed_dim, hidden_size, batch_first=True)

    def forward(self, input_ids, lengths=None):
        emb = self.embedding(input_ids)                     # (B, T, E)
        _, h = self.rnn(emb)                                # h: (num_layers, B, H)
        return self.head(h[-1])


class TfidfSgdClassifier:
    """TF-IDF vectorizer + online SGD linear classifier (baseline).

    The vectorizer is fit once on training text only (no labels, no test data).
    The classifier is initialised with the *full* label list, then updated on
    only the examples that arrive in each stream chunk via ``partial_fit``.
    Passing the full class list on the first update keeps the classifier's
    output space identical across chunks and avoids re-initialising weights
    when a new intent first appears.
    """

    def __init__(self, max_features: int = 50000, ngram_range=(1, 2),
                 lr: float = 0.01, epochs_per_chunk: int = 5,
                 random_state: int = 0):
        self.vectorizer = TfidfVectorizer(max_features=max_features,
                                          ngram_range=ngram_range)
        self.clf = SGDClassifier(loss="log_loss", learning_rate="optimal",
                                 random_state=random_state)
        self.classes_ = None
        self.max_features = max_features
        self.epochs_per_chunk = epochs_per_chunk
        self._fit = False
        self.partial_fit_calls = 0

    def fit_vectorizer(self, texts):
        self.vectorizer.fit(texts)
        self._fit = True

    def initialize_classes(self, labels):
        """Fix the output space to the full label list before any update."""
        self.classes_ = np.array(sorted(set(labels)), dtype=object)

    def partial_fit(self, texts, labels, classes=None):
        if not self._fit:
            raise RuntimeError("call fit_vectorizer on the training corpus first")
        if self.classes_ is None:
            if classes is None:
                raise RuntimeError("classes must be supplied on the first update")
            self.initialize_classes(classes)
        else:
            # grow classes_ to include any newly-arrived intents
            new_classes = np.array(sorted(set(classes)), dtype=object) if classes is not None else None
            if new_classes is not None:
                self.classes_ = np.union1d(self.classes_, new_classes)
        X = self.vectorizer.transform(texts)
        labels = np.array(labels)
        # sklearn's SGDClassifier needs classes= only on the very first call.
        if not hasattr(self.clf, "coef_"):
            self.clf.partial_fit(X, labels, classes=self.classes_)
        else:
            self.clf.partial_fit(X, labels)
        self.partial_fit_calls += 1

    def predict(self, texts):
        X = self.vectorizer.transform(texts)
        return self.clf.predict(X)

    def predict_proba(self, texts):
        X = self.vectorizer.transform(texts)
        return self.clf.predict_proba(X)

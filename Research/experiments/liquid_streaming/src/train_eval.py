"""Class-incremental train/eval loop for the liquid streaming study.

Protocol (stream / sequential continual learning):
  * The 150 CLINC150 intents are split into 5 fixed class-incremental chunks (30 intents each).
  * At chunk step ``i`` the model is trained ONLY on chunk ``i``'s training data (the arriving
    stream), continuing from weights learned on earlier chunks (class-incremental head growth).
  * After training on chunk ``i``, the model is evaluated on the TEST data of every seen chunk
    ``0..i``.  This measures adaptation (new chunk ``i``) and retention (earlier chunks).
  * Validation (chunk ``i`` val) is used for early stopping only.  Test is never used for
    training, tuning, or early stopping.

Outputs (under <run_dir>/):
  raw_results.csv   one row per (seed, model, chunk_step, eval_chunk)
  run_manifest.json full run settings
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.linear_model import SGDClassifier
from torch.utils.data import DataLoader, Dataset

from data import load_intent_dataset
from tokenizer import SimpleTokenizer
from chunks import create_class_incremental_chunks
from models import CfcTextClassifier, LSTMTextClassifier, GRUTextClassifier, TfidfSgdClassifier

MODEL_FACTORY = {
    "lstm": LSTMTextClassifier,
    "gru": GRUTextClassifier,
}


class TextDataset(Dataset):
    def __init__(self, pairs, tokenizer, label_to_idx, max_len=64):
        self.pairs = pairs
        self.tokenizer = tokenizer
        self.label_to_idx = label_to_idx
        self.max_len = max_len

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        text, label = self.pairs[idx]
        label = self.label_to_idx[label]
        ids = self.tokenizer.encode(text, max_len=self.max_len)
        if len(ids) < self.max_len:
            ids = [self.tokenizer.pad_id] * (self.max_len - len(ids)) + ids  # left-pad: last timestep is real token
        else:
            ids = ids[-self.max_len:]  # keep last tokens
        return torch.tensor(ids, dtype=torch.long), label


def collate_fn(batch):
    ids = torch.stack([b[0] for b in batch])
    labels = torch.tensor([b[1] for b in batch], dtype=torch.long)
    return ids, labels


def set_seed(seed: int):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def evaluate_nn(model, pairs, tokenizer, label_to_idx, batch_size=64, max_len=64):
    if len(pairs) == 0:
        return 0.0, 0
    model.eval()
    ds = TextDataset(pairs, tokenizer, label_to_idx, max_len=max_len)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)
    correct = 0
    total = 0
    with torch.no_grad():
        for ids, y in dl:
            logits = model(ids)
            pred = logits.argmax(dim=1)
            correct += int((pred == y).sum().item())
            total += int(y.size(0))
    return (correct / total if total else 0.0), total


def train_chunk_nn(model, train_pairs, val_pairs, tokenizer, label_to_idx,
                   epochs=10, lr=1e-3, batch_size=32, patience=2, max_len=64, seed=0):
    """Train the neural model on one chunk; early stop on chunk val; restore best."""
    set_seed(seed)
    model.train()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    crit = nn.CrossEntropyLoss()

    if len(train_pairs) == 0:
        return 0.0

    ds_train = TextDataset(train_pairs, tokenizer, label_to_idx, max_len=max_len)
    dl_train = DataLoader(ds_train, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)

    best_state = None
    best_val = -1.0
    patience_left = patience

    for epoch in range(epochs):
        model.train()
        for ids, y in dl_train:
            opt.zero_grad()
            logits = model(ids)
            loss = crit(logits, y)
            loss.backward()
            opt.step()

        if len(val_pairs):
            val_acc, _ = evaluate_nn(model, val_pairs, tokenizer, label_to_idx,
                                     batch_size=batch_size, max_len=max_len)
        else:
            val_acc = 0.0

        if val_acc > best_val:
            best_val = val_acc
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            patience_left = patience
        else:
            patience_left -= 1
            if patience_left <= 0:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return best_val


def eval_sgd(clf, pairs, label_to_idx):
    if len(pairs) == 0:
        return 0.0, 0
    texts = [t for t, _ in pairs]
    y_true = np.array([label_to_idx[l] for t, l in pairs])
    pred_strings = clf.predict(texts)
    y_pred = np.array([label_to_idx.get(l, -1) for l in pred_strings])
    correct = int((y_pred == y_true).sum().item())
    return correct / max(1, len(y_true)), len(y_true)
def run_study(data_dir: Path, run_dir: Path, seeds=(0, 1, 2, 3, 4),
              num_chunks: int = 5, chunk_seed: int = 12345,
              embed_dim: int = 64, hidden_size: int = 64,
              batch_size: int = 32, lr: float = 1e-3, max_epochs: int = 10,
              patience: int = 2, max_len: int = 64,
              sgd_epochs_per_chunk: int = 5, sgd_max_features: int = 50000):
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    ds = load_intent_dataset(data_dir)
    dataset_name = ds["name"]
    train_all = ds["train"]
    val_all = ds["val"]
    test_all = ds["test"]

    tokenizer = SimpleTokenizer([t for t, _ in train_all], min_freq=1)
    chunks, intent_order = create_class_incremental_chunks(train_all, num_chunks=num_chunks, seed=chunk_seed)

    intent_to_chunk = {}
    for c in chunks:
        for lab in c["labels"]:
            intent_to_chunk[lab] = c["chunk_id"]

    def split_by_chunk(pairs):
        out = {i: [] for i in range(num_chunks)}
        for t, lab in pairs:
            if lab in intent_to_chunk:
                out[intent_to_chunk[lab]].append((t, lab))
        return out

    val_by_chunk = split_by_chunk(val_all)
    test_by_chunk = split_by_chunk(test_all)

    sgd = TfidfSgdClassifier(epochs_per_chunk=sgd_epochs_per_chunk,
                             max_features=sgd_max_features)
    sgd.fit_vectorizer([t for t, _ in train_all])

    model_names = ["lstm", "gru", "tfidf_sgd"]
    rows = []
    run_id = time.strftime("%Y%m%d-%H%M%S")

    for seed in seeds:
        nn_models = {name: MODEL_FACTORY[name](
            vocab_size=tokenizer.vocab_size, embed_dim=embed_dim,
            hidden_size=hidden_size, num_classes=0, pad_id=tokenizer.pad_id)
            for name in ("lstm", "gru")}
        sgd_seed = TfidfSgdClassifier(epochs_per_chunk=sgd_epochs_per_chunk,
                                      max_features=sgd_max_features)
        sgd_seed.vectorizer = sgd.vectorizer
        sgd_seed.clf = SGDClassifier(loss="log_loss", learning_rate="optimal",
                                     random_state=seed)
        sgd_seed._fit = True
        sgd_seed.classes_ = None
        sgd_seed.initialize_classes(intent_order)

        classes_seen: List[str] = []
        for chunk_id in range(num_chunks):

            chunk = chunks[chunk_id]
            chunk_labels = sorted(chunk["labels"])
            classes_seen = sorted(set(classes_seen) | set(chunk_labels))
            n_classes = len(classes_seen)
            label_to_idx = {lab: i for i, lab in enumerate(classes_seen)}

            train_pairs = chunk["train"]
            val_pairs = val_by_chunk[chunk_id]

            # neural models
            for name in ("lstm", "gru"):
                model = nn_models[name]
                model.set_num_classes(n_classes)
                train_chunk_nn(model, train_pairs, val_pairs, tokenizer, label_to_idx,
                               epochs=max_epochs, lr=lr, batch_size=batch_size,
                               patience=patience, max_len=max_len, seed=seed)
                for eval_chunk_id in range(chunk_id + 1):
                    eval_pairs = [(t, l) for t, l in test_by_chunk[eval_chunk_id]
                                  if l in label_to_idx]
                    acc, n = evaluate_nn(model, eval_pairs, tokenizer, label_to_idx,
                                         batch_size=batch_size, max_len=max_len)
                    rows.append({
                        "run_id": run_id, "seed": seed, "model": name,
                        "chunk_step": chunk_id, "eval_chunk": eval_chunk_id,
                        "accuracy": acc, "n_classes_seen": n_classes,
                        "n_train_examples": len(train_pairs),
                        "n_eval_examples": n,
                    })

            # tfidf+sgd
            train_texts = [t for t, _ in train_pairs]
            train_labels = [l for _, l in train_pairs]
            sgd_seed.partial_fit(train_texts, train_labels)
            for eval_chunk_id in range(chunk_id + 1):
                eval_pairs = [(t, l) for t, l in test_by_chunk[eval_chunk_id]
                              if l in label_to_idx]
                acc, n = eval_sgd(sgd_seed, eval_pairs, label_to_idx)
                rows.append({
                    "run_id": run_id, "seed": seed, "model": "tfidf_sgd",
                    "chunk_step": chunk_id, "eval_chunk": eval_chunk_id,
                    "accuracy": acc, "n_classes_seen": n_classes,
                    "n_train_examples": len(train_pairs),
                    "n_eval_examples": n,
                })

    csv_path = run_dir / "raw_results.csv"
    fieldnames = ["run_id", "seed", "model", "chunk_step", "eval_chunk",
                  "accuracy", "n_classes_seen", "n_train_examples", "n_eval_examples"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    manifest = {
        "run_id": run_id,
        "dataset": dataset_name,
        "num_chunks": num_chunks,
        "chunk_seed": chunk_seed,
        "seeds": list(seeds),
        "intent_order": intent_order,
        "chunks": {str(c["chunk_id"]): c["labels"] for c in chunks},
        "splits": {"train": len(train_all), "val": len(val_all), "test": len(test_all)},
        "vocab_size": tokenizer.vocab_size,
        "models": model_names,
        "embed_dim": embed_dim, "hidden_size": hidden_size,
        "batch_size": batch_size, "lr": lr, "max_epochs": max_epochs,
        "patience": patience, "max_len": max_len,
        "sgd_epochs_per_chunk": sgd_epochs_per_chunk, "sgd_max_features": sgd_max_features,
        "n_raw_rows": len(rows),
        "elapsed_seconds": time.time() - t0,
        "note": "Sequential class-incremental protocol: train on arriving chunk only, evaluate on all seen chunks' test. Val used for early stopping only; test never used for training/tuning.",
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"study done: {len(rows)} raw rows -> {csv_path}")
    return rows, manifest


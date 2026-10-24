from __future__ import annotations

import json
import os
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

from tokenizer import SimpleTokenizer
from data import load_intent_dataset
from chunks import create_class_incremental_chunks
from model_cfc import CfcTextClassifier

class TextDataset(Dataset):
    def __init__(self, pairs, tokenizer, max_len=64):
        self.pairs = pairs
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        text, label = self.pairs[idx]
        ids = self.tokenizer.encode(text, max_len=self.max_len)
        if len(ids) < self.max_len:
            ids = ids + [self.tokenizer.pad_id] * (self.max_len - len(ids))
        else:
            ids = ids[: self.max_len]
        return torch.tensor(ids, dtype=torch.long), label


def collate_fn(batch):
    ids = torch.stack([b[0] for b in batch])
    labels = [b[1] for b in batch]
    return ids, labels


def run_smoke(outdir: Path = None):
    root = Path(__file__).resolve().parents[1]
    if outdir is None:
        outdir = root / "out_smoke"
    outdir.mkdir(parents=True, exist_ok=True)
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    ds = load_intent_dataset(data_dir)
    dataset_name = ds["name"]
    train_all = ds["train"]
    val_all = ds["val"]
    test_all = ds["test"]

    tokenizer = SimpleTokenizer([t for t, _ in train_all], min_freq=1)
    import pickle

    tok_path = outdir / "tokenizer.pkl"
    with tok_path.open("wb") as f:
        pickle.dump(tokenizer, f)

    chunks, intent_order = create_class_incremental_chunks(train_all, num_chunks=5, seed=12345)
    chunks_meta = {
        "intent_order": intent_order,
        "num_chunks": 5,
        "chunks": [{"chunk_id": c["chunk_id"], "labels": c["labels"], "num_train": len(c["train"])} for c in chunks],
        "splits": {"train": len(train_all), "val": len(val_all), "test": len(test_all)},
        "dataset": dataset_name,
    }
    (outdir / "chunks_meta.json").write_text(json.dumps(chunks_meta, indent=2), encoding="utf-8")

    chunk0 = chunks[0]
    train_pairs = chunk0["train"][:20]
    test_pairs = test_all[:20]

    all_labels = sorted(list(set([l for _, l in train_pairs] + [l for _, l in test_pairs] + chunk0["labels"])))
    label_to_idx = {l: i for i, l in enumerate(all_labels)}

    model = CfcTextClassifier(vocab_size=tokenizer.vocab_size, embed_dim=64, hidden_size=64, num_classes=len(all_labels), pad_id=tokenizer.pad_id)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    crit = nn.CrossEntropyLoss()

    ds_train = TextDataset(train_pairs, tokenizer)
    dl_train = DataLoader(ds_train, batch_size=8, shuffle=True, collate_fn=collate_fn)

    model.train()
    for epoch in range(1):
        for ids, labels in dl_train:
            y = torch.tensor([label_to_idx.get(l, 0) for l in labels], dtype=torch.long)
            opt.zero_grad()
            logits = model(ids)
            loss = crit(logits, y)
            loss.backward()
            opt.step()

    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        ds_test = TextDataset(test_pairs, tokenizer)
        dl_test = DataLoader(ds_test, batch_size=16, shuffle=False, collate_fn=collate_fn)
        for ids, labels in dl_test:
            y = torch.tensor([label_to_idx.get(l, 0) for l in labels], dtype=torch.long)
            logits = model(ids)
            pred = logits.argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)
    acc = correct / total if total > 0 else 0.0

    ncps_version = "unknown"
    try:
        import ncps
        ncps_version = getattr(ncps, "__version__", ncps_version)
    except Exception:
        pass
    try:
        from importlib.metadata import version
        ncps_version = version("ncps")
    except Exception:
        pass

    result_row = {
        "dataset": dataset_name,
        "ncps_version": ncps_version,
        "chunk_trained": 0,
        "train_examples": len(train_pairs),
        "test_examples": len(test_pairs),
        "accuracy": acc,
        "timestamp": time.time(),
        "vocab_size": tokenizer.vocab_size,
        "num_classes": len(all_labels),
    }
    res_path = outdir / "result_row.json"
    res_path.write_text(json.dumps(result_row, indent=2), encoding="utf-8")

    meta = {
        "run_metadata": result_row,
        "chunks_meta": chunks_meta,
        "artifacts": {
            "tokenizer": str(tok_path),
            "chunks_meta": str(outdir / "chunks_meta.json"),
            "result_row": str(res_path),
        },
    }
    meta_path = outdir / "run_metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return result_row

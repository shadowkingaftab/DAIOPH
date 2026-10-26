"""Class-incremental train/eval loop for the liquid streaming study.

Protocol (stream / sequential continual learning):
  * The 150 CLINC150 intents are split into 5 fixed class-incremental chunks
    (30 intents each).
  * At chunk step ``i`` the model is trained ONLY on chunk ``i``'s training data
    (the arriving stream), continuing from weights learned on earlier chunks
    (class-incremental head growth).
  * After training on chunk ``i``, the model is evaluated on the TEST data of
    every seen chunk ``0..i``.  This measures adaptation (new chunk ``i``) and
    retention (earlier chunks).
  * Validation (chunk ``i`` val) is used for early stopping and for fitting
    temperature scaling only.  Test is never used for training, tuning or
    calibration fitting.

Models:
  * cfc                    -- ncps CfC, default mode
  * cfc_ablation_pure      -- ncps CfC ablation, mode="pure"
  * cfc_ablation_no_gate   -- ncps CfC ablation, mode="no_gate"
  * lstm                   -- LSTM baseline
  * gru                    -- GRU baseline
  * tfidf_sgd              -- TF-IDF + SGD classifier baseline

Outputs (under <run_dir>/):
  raw_results.csv             one row per (seed, model, chunk_step, eval_chunk)
  per_example_predictions.csv one row per scored test example
  learning_curves.csv         validation learning curve per epoch/chunk
  model_metrics.csv           parameter count, serialized size, CPU latency
  failures.csv                any cell that failed (empty header if none)
  status.json                 incremental run status
  run_manifest.json           full provenance/config, written at the end
"""
from __future__ import annotations

import csv
import io
import json
import math
import os
import pickle
import random
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.linear_model import SGDClassifier
from torch.utils.data import DataLoader, Dataset

from calibration import apply_temperature, compute_ece, fit_temperature, softmax
from chunks import create_class_incremental_chunks
from data import load_intent_dataset
from models import (CfcTextClassifier, GRUTextClassifier, LSTMTextClassifier,
                    TfidfSgdClassifier)
from study_utils import (dataset_integrity, environment_info,
                         source_revision, utc_now)
from tokenizer import SimpleTokenizer

MODEL_SPECS: Dict[str, Dict[str, Any]] = {
    "cfc": {"family": "cfc", "mode": "default"},
    "cfc_ablation_pure": {"family": "cfc", "mode": "pure"},
    "cfc_ablation_no_gate": {"family": "cfc", "mode": "no_gate"},
    "lstm": {"family": "lstm"},
    "gru": {"family": "gru"},
    "tfidf_sgd": {"family": "sgd"},
}
NEURAL_MODEL_NAMES = tuple(k for k, v in MODEL_SPECS.items() if v["family"] != "sgd")
ALL_MODEL_NAMES = tuple(MODEL_SPECS)

RAW_FIELDS = [
    "run_id", "seed", "model", "model_family", "cfc_mode",
    "chunk_step", "eval_chunk", "accuracy", "n_eval_correct",
    "n_classes_seen", "model_output_classes", "n_train_examples",
    "n_eval_examples", "temperature", "calibration_applied",
    "ece_calibrated", "brier_calibrated", "ece_uncalibrated",
    "brier_uncalibrated", "n_calibration_bins", "sgd_epochs_completed",
]
PER_EXAMPLE_FIELDS = [
    "run_id", "seed", "model", "chunk_step", "eval_chunk", "example_idx",
    "true_label", "true_label_idx", "pred_label", "pred_label_idx", "correct",
    "confidence_uncalibrated", "prob_true_uncalibrated",
    "confidence_calibrated", "prob_true_calibrated", "calibrated",
    "temperature", "model_output_classes",
]
LEARNING_FIELDS = [
    "run_id", "seed", "model", "chunk_step", "epoch", "train_loss",
    "val_accuracy", "stopped_early", "n_train_examples",
]
MODEL_METRIC_FIELDS = [
    "run_id", "seed", "model", "n_params", "serialized_size_mb",
    "latency_p50_ms", "latency_p95_ms", "latency_mean_ms",
    "throughput_examples_per_sec", "warmup_examples", "measured_examples",
    "latency_scope", "batch_size", "n_features",
]
FAILURE_FIELDS = ["run_id", "seed", "model", "chunk_step", "stage", "error",
                  "traceback"]


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
            ids = [self.tokenizer.pad_id] * (self.max_len - len(ids)) + ids
        else:
            ids = ids[-self.max_len:]
        return torch.tensor(ids, dtype=torch.long), label


def collate_fn(batch):
    ids = torch.stack([b[0] for b in batch])
    labels = torch.tensor([b[1] for b in batch], dtype=torch.long)
    return ids, labels


def set_seed(seed: int):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass


def _label_index(label_to_idx: Dict[str, int]) -> List[str]:
    idx_to_label = [None] * len(label_to_idx)
    for label, idx in label_to_idx.items():
        idx_to_label[idx] = label
    return idx_to_label


def evaluate_nn_simple(model, pairs, tokenizer, label_to_idx, batch_size=64,
                       max_len=64):
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


def collect_nn_logits(model, pairs, tokenizer, label_to_idx, batch_size=64,
                      max_len=64) -> Tuple[np.ndarray, np.ndarray]:
    model.eval()
    ds = TextDataset(pairs, tokenizer, label_to_idx, max_len=max_len)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)
    logits_list: List[np.ndarray] = []
    labels_list: List[np.ndarray] = []
    with torch.no_grad():
        for ids, y in dl:
            logits_list.append(model(ids).cpu().numpy())
            labels_list.append(y.cpu().numpy())
    if not logits_list:
        return np.zeros((0, 0)), np.zeros((0,), dtype=int)
    return np.concatenate(logits_list, axis=0), np.concatenate(labels_list, axis=0)


def evaluate_nn_detailed(model, pairs, tokenizer, label_to_idx, batch_size=64,
                         max_len=64, temperature: float = 1.0,
                         calibrated: bool = False, n_bins: int = 15) -> Dict[str, Any]:
    """Return accuracy, ECE/Brier and per-example (un)calibrated probabilities."""
    if len(pairs) == 0:
        return {"accuracy": 0.0, "n": 0, "per_example": [],
                "ece_calibrated": float("nan"), "brier_calibrated": float("nan"),
                "ece_uncalibrated": float("nan"), "brier_uncalibrated": float("nan")}
    idx_to_label = _label_index(label_to_idx)
    model.eval()
    ds = TextDataset(pairs, tokenizer, label_to_idx, max_len=max_len)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)
    correct = 0
    total = 0
    example_offset = 0
    per_example: List[Dict[str, Any]] = []
    probs_uncal_all: List[np.ndarray] = []
    probs_cal_all: List[np.ndarray] = []
    labels_all: List[np.ndarray] = []
    with torch.no_grad():
        for ids, y in dl:
            logits = model(ids)
            pred = logits.argmax(dim=1)
            correct += int((pred == y).sum().item())
            total += int(y.size(0))
            logits_np = logits.cpu().numpy()
            probs_uncal = softmax(logits_np, axis=1)
            probs_cal = apply_temperature(logits_np, temperature)
            y_np = y.cpu().numpy()
            pred_np = pred.cpu().numpy()
            probs_uncal_all.append(probs_uncal)
            probs_cal_all.append(probs_cal)
            labels_all.append(y_np)
            for j in range(len(y_np)):
                per_example.append({
                    "example_idx": example_offset + j,
                    "true_label": idx_to_label[int(y_np[j])],
                    "true_label_idx": int(y_np[j]),
                    "pred_label": idx_to_label[int(pred_np[j])],
                    "pred_label_idx": int(pred_np[j]),
                    "correct": int(pred_np[j] == y_np[j]),
                    "confidence_uncalibrated": float(probs_uncal[j].max()),
                    "prob_true_uncalibrated": float(probs_uncal[j, y_np[j]]),
                    "confidence_calibrated": float(probs_cal[j].max()),
                    "prob_true_calibrated": float(probs_cal[j, y_np[j]]),
                    "calibrated": bool(calibrated),
                })
            example_offset += len(y_np)
    probs_uncal = np.concatenate(probs_uncal_all, axis=0)
    probs_cal = np.concatenate(probs_cal_all, axis=0)
    labels = np.concatenate(labels_all, axis=0)
    met_uncal = compute_ece(probs_uncal, labels, n_bins=n_bins)
    met_cal = compute_ece(probs_cal, labels, n_bins=n_bins)
    acc = (correct / total if total else 0.0)
    return {
        "accuracy": acc, "n": total, "n_correct": correct,
        "per_example": per_example,
        "ece_calibrated": met_cal["ece"], "brier_calibrated": met_cal["brier"],
        "ece_uncalibrated": met_uncal["ece"], "brier_uncalibrated": met_uncal["brier"],
    }


def train_chunk_nn(model, train_pairs, val_pairs, tokenizer, label_to_idx,
                   epochs=10, lr=1e-3, batch_size=32, patience=2, max_len=64,
                   seed=0) -> Tuple[float, List[Dict[str, Any]]]:
    """Train on one chunk, early stop on chunk val, restore best weights."""
    set_seed(seed)
    model.train()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    crit = nn.CrossEntropyLoss()
    history: List[Dict[str, Any]] = []

    if len(train_pairs) == 0:
        return 0.0, history

    ds_train = TextDataset(train_pairs, tokenizer, label_to_idx, max_len=max_len)
    generator = torch.Generator()
    generator.manual_seed(int(seed))
    dl_train = DataLoader(ds_train, batch_size=batch_size, shuffle=True,
                          collate_fn=collate_fn, generator=generator)

    best_state = None
    best_val = -1.0
    patience_left = patience
    stopped_early = False

    for epoch in range(epochs):
        model.train()
        loss_sum = 0.0
        n_batches = 0
        for ids, y in dl_train:
            opt.zero_grad()
            logits = model(ids)
            loss = crit(logits, y)
            loss.backward()
            opt.step()
            loss_sum += float(loss.detach().item())
            n_batches += 1

        if len(val_pairs):
            val_acc, _ = evaluate_nn_simple(model, val_pairs, tokenizer,
                                            label_to_idx, batch_size=batch_size,
                                            max_len=max_len)
        else:
            val_acc = 0.0
        history.append({
            "epoch": epoch + 1,
            "train_loss": (loss_sum / n_batches if n_batches else float("nan")),
            "val_accuracy": val_acc,
            "stopped_early": False,
        })

        if val_acc > best_val:
            best_val = val_acc
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            patience_left = patience
        else:
            patience_left -= 1
            if patience_left <= 0:
                stopped_early = True
                history[-1]["stopped_early"] = True
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return best_val, history


def eval_sgd_simple(clf, pairs, label_to_idx):
    if len(pairs) == 0:
        return 0.0, 0
    texts = [t for t, _ in pairs]
    pred_strings = clf.predict(texts)
    correct = sum(int(p == l) for p, (_, l) in zip(pred_strings, pairs))
    return correct / max(1, len(pairs)), len(pairs)


def _sgd_class_indices(clf) -> Dict[str, int]:
    return {str(c): i for i, c in enumerate(clf.classes_)}


def evaluate_sgd_detailed(clf, pairs, label_to_idx, temperature: float = 1.0,
                          calibrated: bool = False, n_bins: int = 15) -> Dict[str, Any]:
    if len(pairs) == 0:
        return {"accuracy": 0.0, "n": 0, "per_example": [],
                "ece_calibrated": float("nan"), "brier_calibrated": float("nan"),
                "ece_uncalibrated": float("nan"), "brier_uncalibrated": float("nan")}
    idx_to_label = _label_index(label_to_idx)
    texts = [t for t, _ in pairs]
    true_strings = [l for _, l in pairs]
    X = clf.vectorizer.transform(texts)
    log_probs = clf.clf.predict_log_proba(X)
    probs_uncal = np.exp(log_probs)
    probs_cal = apply_temperature(log_probs, temperature)
    clf_classes = [str(c) for c in clf.clf.classes_]
    class_to_idx = {c: i for i, c in enumerate(clf_classes)}
    true_clf_idx = np.array([class_to_idx[s] for s in true_strings], dtype=int)
    pred_strings = [clf_classes[i] for i in probs_cal.argmax(axis=1)]
    correct = sum(int(p == l) for p, l in zip(pred_strings, true_strings))
    per_example: List[Dict[str, Any]] = []
    for j, (true_s, pred_s) in enumerate(zip(true_strings, pred_strings)):
        per_example.append({
            "example_idx": j,
            "true_label": true_s,
            "true_label_idx": int(label_to_idx.get(true_s, -1)),
            "pred_label": pred_s,
            "pred_label_idx": int(label_to_idx.get(pred_s, -1)),
            "correct": int(pred_s == true_s),
            "confidence_uncalibrated": float(probs_uncal[j].max()),
            "prob_true_uncalibrated": float(probs_uncal[j, true_clf_idx[j]]),
            "confidence_calibrated": float(probs_cal[j].max()),
            "prob_true_calibrated": float(probs_cal[j, true_clf_idx[j]]),
            "calibrated": bool(calibrated),
        })
    met_uncal = compute_ece(probs_uncal, true_clf_idx, n_bins=n_bins)
    met_cal = compute_ece(probs_cal, true_clf_idx, n_bins=n_bins)
    return {
        "accuracy": correct / max(1, len(pairs)), "n": len(pairs),
        "n_correct": correct, "per_example": per_example,
        "ece_calibrated": met_cal["ece"], "brier_calibrated": met_cal["brier"],
        "ece_uncalibrated": met_uncal["ece"], "brier_uncalibrated": met_uncal["brier"],
    }


def fit_sgd_temperature(clf, val_pairs) -> float:
    if not val_pairs:
        return 1.0
    texts = [t for t, _ in val_pairs]
    true_strings = [l for _, l in val_pairs]
    class_to_idx = _sgd_class_indices(clf.clf)
    labels = np.array([class_to_idx[s] for s in true_strings], dtype=int)
    log_probs = clf.clf.predict_log_proba(clf.vectorizer.transform(texts))
    return float(fit_temperature(log_probs, labels))


def train_sgd_chunk(clf, train_pairs, val_pairs, label_to_idx, seed: int,
                    chunk_id: int, epochs: int) -> Tuple[List[Dict[str, Any]], float]:
    history: List[Dict[str, Any]] = []
    if not train_pairs:
        return history, 1.0
    texts = [t for t, _ in train_pairs]
    labels = [l for _, l in train_pairs]
    for epoch in range(epochs):
        rng = random.Random(int(seed) * 1_000_000 + int(chunk_id) * 10_000 + epoch)
        order = list(range(len(texts)))
        rng.shuffle(order)
        ep_texts = [texts[i] for i in order]
        ep_labels = [labels[i] for i in order]
        clf.partial_fit(ep_texts, ep_labels)
        val_acc, _ = eval_sgd_simple(clf, val_pairs, label_to_idx)
        history.append({
            "epoch": epoch + 1,
            "train_loss": float("nan"),
            "val_accuracy": val_acc,
            "stopped_early": False,
        })
    temperature = fit_sgd_temperature(clf, val_pairs)
    return history, temperature


def build_neural_model(name: str, vocab_size: int, embed_dim: int, hidden_size: int,
                       pad_id: int) -> nn.Module:
    spec = MODEL_SPECS[name]
    if spec["family"] == "cfc":
        return CfcTextClassifier(vocab_size=vocab_size, embed_dim=embed_dim,
                                 hidden_size=hidden_size, num_classes=0,
                                 pad_id=pad_id, mode=spec["mode"],
                                 mixed_memory=False)
    if spec["family"] == "lstm":
        return LSTMTextClassifier(vocab_size=vocab_size, embed_dim=embed_dim,
                                  hidden_size=hidden_size, num_classes=0,
                                  pad_id=pad_id)
    if spec["family"] == "gru":
        return GRUTextClassifier(vocab_size=vocab_size, embed_dim=embed_dim,
                                 hidden_size=hidden_size, num_classes=0,
                                 pad_id=pad_id)
    raise ValueError(f"not a neural model: {name}")


def _tokenize_one(text: str, tokenizer: SimpleTokenizer, max_len: int) -> torch.Tensor:
    ids = tokenizer.encode(text, max_len=max_len)
    if len(ids) < max_len:
        ids = [tokenizer.pad_id] * (max_len - len(ids)) + ids
    else:
        ids = ids[-max_len:]
    return torch.tensor([ids], dtype=torch.long)


def measure_model_metrics(name: str, seed: int, run_id: str, model, sgd_clf,
                          tokenizer: SimpleTokenizer, texts: Sequence[str],
                          max_len: int, warmup: int, measured: int) -> Dict[str, Any]:
    import io
    import pickle
    import time as _time

    n_params = 0
    n_features = None
    if MODEL_SPECS[name]["family"] == "sgd":
        n_params = int(sgd_clf.clf.coef_.size + sgd_clf.clf.intercept_.size)
        n_features = int(len(sgd_clf.vectorizer.vocabulary_))
        payload = pickle.dumps({"vectorizer": sgd_clf.vectorizer, "clf": sgd_clf.clf})
        size_mb = len(payload) / 1_000_000.0

        def predict_one(text: str):
            return sgd_clf.clf.predict(sgd_clf.vectorizer.transform([text]))[0]
    else:
        n_params = int(sum(p.numel() for p in model.parameters()))
        buf = io.BytesIO()
        torch.save({k: v.detach().cpu() for k, v in model.state_dict().items()}, buf)
        size_mb = len(buf.getvalue()) / 1_000_000.0
        model.eval()

        def predict_one(text: str):
            ids = _tokenize_one(text, tokenizer, max_len)
            with torch.no_grad():
                return int(model(ids).argmax(dim=1).item())

    seq = list(texts)
    if seq:
        for i in range(max(0, int(warmup))):
            predict_one(seq[i % len(seq)])
        measured = min(int(measured), max(1, len(seq) * 4))
        times = []
        for i in range(int(measured)):
            text = seq[i % len(seq)]
            t0 = _time.perf_counter()
            predict_one(text)
            times.append((_time.perf_counter() - t0) * 1000.0)
    else:
        measured = 0
        times = [float("nan")]
    arr = np.array(times, dtype=float)
    mean_ms = float(np.nanmean(arr)) if len(arr) else float("nan")
    return {
        "run_id": run_id, "seed": int(seed), "model": name,
        "n_params": n_params, "serialized_size_mb": float(size_mb),
        "latency_p50_ms": float(np.nanpercentile(arr, 50)) if len(arr) else float("nan"),
        "latency_p95_ms": float(np.nanpercentile(arr, 95)) if len(arr) else float("nan"),
        "latency_mean_ms": mean_ms,
        "throughput_examples_per_sec": (1000.0 / mean_ms if mean_ms and np.isfinite(mean_ms) else float("nan")),
        "warmup_examples": int(warmup), "measured_examples": int(measured),
        "latency_scope": "single-example end-to-end text->prediction on CPU; tokenization/vectorization included; batch_size=1",
        "batch_size": 1, "n_features": n_features,
    }


def _write_csv(path: Path, rows: Sequence[Dict[str, Any]], fields: Sequence[str]) -> None:
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_study(data_dir: Path, run_dir: Path, seeds=(0, 1, 2, 3, 4),
              num_chunks: int = 5, chunk_seed: int = 12345,
              embed_dim: int = 64, hidden_size: int = 64,
              batch_size: int = 32, lr: float = 1e-3, max_epochs: int = 10,
              patience: int = 2, max_len: int = 64,
              sgd_epochs_per_chunk: int = 5, sgd_max_features: int = 50000,
              calibrate: bool = True, save_per_example: bool = True,
              n_bins: int = 15, latency_examples: int = 100,
              latency_warmup: int = 5, models: Optional[Sequence[str]] = None,
              run_id: Optional[str] = None, command: Optional[str] = None):
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    run_id = run_id or time.strftime("%Y%m%d-%H%M%S")
    selected_models = tuple(models) if models else ALL_MODEL_NAMES
    unknown = [m for m in selected_models if m not in MODEL_SPECS]
    if unknown:
        raise ValueError(f"unknown models: {unknown}")
    started_at = utc_now()
    t0 = time.time()

    ds = load_intent_dataset(Path(data_dir))
    dataset_name = ds["name"]
    train_all = ds["train"]
    val_all = ds["val"]
    test_all = ds["test"]

    tokenizer = SimpleTokenizer([t for t, _ in train_all], min_freq=1)
    chunks, intent_order = create_class_incremental_chunks(
        train_all, num_chunks=num_chunks, seed=chunk_seed)
    full_label_list = sorted(set(label for _, label in train_all))

    intent_to_chunk: Dict[str, int] = {}
    for c in chunks:
        for lab in c["labels"]:
            intent_to_chunk[lab] = c["chunk_id"]

    def split_by_chunk(pairs):
        out = {i: [] for i in range(num_chunks)}
        for t, lab in pairs:
            if lab in intent_to_chunk:
                out[int(intent_to_chunk[lab])].append((t, lab))
        return out

    val_by_chunk = split_by_chunk(val_all)
    test_by_chunk = split_by_chunk(test_all)

    master_sgd = TfidfSgdClassifier(epochs_per_chunk=sgd_epochs_per_chunk,
                                    max_features=sgd_max_features)
    master_sgd.fit_vectorizer([t for t, _ in train_all])

    raw_rows: List[Dict[str, Any]] = []
    per_example_rows: List[Dict[str, Any]] = []
    learning_rows: List[Dict[str, Any]] = []
    model_metric_rows: List[Dict[str, Any]] = []
    failure_rows: List[Dict[str, Any]] = []

    expected_cells = len(selected_models) * len(seeds) * sum(
        range(1, num_chunks + 1))
    completed_cells = 0

    raw_path = run_dir / "raw_results.csv"
    per_example_path = run_dir / "per_example_predictions.csv"
    learning_path = run_dir / "learning_curves.csv"
    metrics_path = run_dir / "model_metrics.csv"
    failures_path = run_dir / "failures.csv"
    status_path = run_dir / "status.json"

    def checkpoint(stage: str, extra: Optional[Dict[str, Any]] = None) -> None:
        _write_csv(raw_path, raw_rows, RAW_FIELDS)
        if save_per_example:
            _write_csv(per_example_path, per_example_rows, PER_EXAMPLE_FIELDS)
        _write_csv(learning_path, learning_rows, LEARNING_FIELDS)
        _write_csv(metrics_path, model_metric_rows, MODEL_METRIC_FIELDS)
        _write_csv(failures_path, failure_rows, FAILURE_FIELDS)
        status = {
            "run_id": run_id,
            "updated_at_utc": utc_now(),
            "stage": stage,
            "completed_cells": len(raw_rows),
            "expected_cells": expected_cells,
            "raw_rows": len(raw_rows),
            "per_example_rows": len(per_example_rows),
            "learning_curve_rows": len(learning_rows),
            "model_metric_rows": len(model_metric_rows),
            "failures": len(failure_rows),
            "completed_all": len(raw_rows) == expected_cells,
        }
        if extra:
            status.update(extra)
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")

    checkpoint("initialised")

    for seed in seeds:
        set_seed(int(seed))
        neural_models: Dict[str, nn.Module] = {}
        for name in selected_models:
            if MODEL_SPECS[name]["family"] == "sgd":
                continue
            set_seed(int(seed))
            neural_models[name] = build_neural_model(
                name, tokenizer.vocab_size, embed_dim, hidden_size, tokenizer.pad_id)

        sgd_model: Optional[TfidfSgdClassifier] = None
        if "tfidf_sgd" in selected_models:
            sgd_model = TfidfSgdClassifier(epochs_per_chunk=sgd_epochs_per_chunk,
                                           max_features=sgd_max_features)
            sgd_model.vectorizer = master_sgd.vectorizer
            sgd_model.clf = SGDClassifier(loss="log_loss", learning_rate="optimal",
                                          random_state=int(seed))
            sgd_model._fit = True
            sgd_model.initialize_classes(full_label_list)

        classes_seen: List[str] = []
        disabled: Dict[str, str] = {}

        for chunk_id in range(num_chunks):
            chunk = chunks[chunk_id]
            chunk_labels = sorted(chunk["labels"])
            classes_seen = sorted(set(classes_seen) | set(chunk_labels))
            label_to_idx = {lab: i for i, lab in enumerate(classes_seen)}
            n_classes = len(classes_seen)
            train_pairs = chunk["train"]
            val_pairs = [(t, l) for t, l in val_by_chunk[chunk_id]
                         if l in label_to_idx]
            training_seed = int(seed) * 1000 + int(chunk_id)

            for name in neural_models:
                model = neural_models[name]
                if name in disabled:
                    continue
                try:
                    model.set_num_classes(n_classes)
                    _, history = train_chunk_nn(
                        model, train_pairs, val_pairs, tokenizer, label_to_idx,
                        epochs=max_epochs, lr=lr, batch_size=batch_size,
                        patience=patience, max_len=max_len, seed=training_seed)
                    for h in history:
                        learning_rows.append({
                            "run_id": run_id, "seed": int(seed), "model": name,
                            "chunk_step": int(chunk_id), **h,
                            "n_train_examples": len(train_pairs),
                        })
                    temperature = 1.0
                    if calibrate and val_pairs:
                        val_logits, val_labels = collect_nn_logits(
                            model, val_pairs, tokenizer, label_to_idx,
                            batch_size=batch_size, max_len=max_len)
                        temperature = float(fit_temperature(val_logits, val_labels))
                    for eval_chunk_id in range(chunk_id + 1):
                        eval_pairs = [(t, l) for t, l in test_by_chunk[eval_chunk_id]
                                      if l in label_to_idx]
                        res = evaluate_nn_detailed(
                            model, eval_pairs, tokenizer, label_to_idx,
                            batch_size=batch_size, max_len=max_len,
                            temperature=temperature,
                            calibrated=bool(calibrate), n_bins=n_bins)
                        raw_rows.append({
                            "run_id": run_id, "seed": int(seed), "model": name,
                            "model_family": MODEL_SPECS[name]["family"],
                            "cfc_mode": MODEL_SPECS[name].get("mode", ""),
                            "chunk_step": int(chunk_id),
                            "eval_chunk": int(eval_chunk_id),
                            "accuracy": res["accuracy"],
                            "n_eval_correct": res.get("n_correct", 0),
                            "n_classes_seen": n_classes,
                            "model_output_classes": n_classes,
                            "n_train_examples": len(train_pairs),
                            "n_eval_examples": res["n"],
                            "temperature": temperature,
                            "calibration_applied": bool(calibrate),
                            "ece_calibrated": res["ece_calibrated"],
                            "brier_calibrated": res["brier_calibrated"],
                            "ece_uncalibrated": res["ece_uncalibrated"],
                            "brier_uncalibrated": res["brier_uncalibrated"],
                            "n_calibration_bins": n_bins,
                            "sgd_epochs_completed": 0,
                        })
                        if save_per_example:
                            for pe in res["per_example"]:
                                per_example_rows.append({
                                    "run_id": run_id, "seed": int(seed),
                                    "model": name, "chunk_step": int(chunk_id),
                                    "eval_chunk": int(eval_chunk_id), **pe,
                                    "temperature": temperature,
                                    "model_output_classes": n_classes,
                                })
                except Exception as e:
                    disabled[name] = str(e)
                    failure_rows.append({
                        "run_id": run_id, "seed": int(seed), "model": name,
                        "chunk_step": int(chunk_id), "stage": "train/eval",
                        "error": str(e), "traceback": traceback.format_exc(),
                    })

            if sgd_model is not None and "tfidf_sgd" not in disabled:
                try:
                    sgd_history, temperature = train_sgd_chunk(
                        sgd_model, train_pairs, val_pairs, label_to_idx,
                        seed=int(seed), chunk_id=int(chunk_id),
                        epochs=sgd_epochs_per_chunk)
                    for h in sgd_history:
                        learning_rows.append({
                            "run_id": run_id, "seed": int(seed),
                            "model": "tfidf_sgd", "chunk_step": int(chunk_id),
                            **h, "n_train_examples": len(train_pairs),
                        })
                    if not calibrate:
                        temperature = 1.0
                    for eval_chunk_id in range(chunk_id + 1):
                        eval_pairs = [(t, l) for t, l in test_by_chunk[eval_chunk_id]
                                      if l in label_to_idx]
                        res = evaluate_sgd_detailed(
                            sgd_model, eval_pairs, label_to_idx,
                            temperature=temperature,
                            calibrated=bool(calibrate), n_bins=n_bins)
                        raw_rows.append({
                            "run_id": run_id, "seed": int(seed),
                            "model": "tfidf_sgd", "model_family": "sgd",
                            "cfc_mode": "", "chunk_step": int(chunk_id),
                            "eval_chunk": int(eval_chunk_id),
                            "accuracy": res["accuracy"],
                            "n_eval_correct": res.get("n_correct", 0),
                            "n_classes_seen": n_classes,
                            "model_output_classes": len(sgd_model.clf.classes_),
                            "n_train_examples": len(train_pairs),
                            "n_eval_examples": res["n"],
                            "temperature": temperature,
                            "calibration_applied": bool(calibrate),
                            "ece_calibrated": res["ece_calibrated"],
                            "brier_calibrated": res["brier_calibrated"],
                            "ece_uncalibrated": res["ece_uncalibrated"],
                            "brier_uncalibrated": res["brier_uncalibrated"],
                            "n_calibration_bins": n_bins,
                            "sgd_epochs_completed": len(sgd_history),
                        })
                        if save_per_example:
                            for pe in res["per_example"]:
                                per_example_rows.append({
                                    "run_id": run_id, "seed": int(seed),
                                    "model": "tfidf_sgd",
                                    "chunk_step": int(chunk_id),
                                    "eval_chunk": int(eval_chunk_id), **pe,
                                    "temperature": temperature,
                                    "model_output_classes": len(sgd_model.clf.classes_),
                                })
                except Exception as e:
                    disabled["tfidf_sgd"] = str(e)
                    failure_rows.append({
                        "run_id": run_id, "seed": int(seed), "model": "tfidf_sgd",
                        "chunk_step": int(chunk_id), "stage": "train/eval",
                        "error": str(e), "traceback": traceback.format_exc(),
                    })

            checkpoint(f"completed seed={seed} chunk_step={chunk_id}")

        # Final model size / latency measurements for this seed.
        latency_texts = [t for t, _ in test_all[:max(1, latency_examples)]]
        for name in selected_models:
            if name in disabled:
                continue
            try:
                metric = measure_model_metrics(
                    name, int(seed), run_id,
                    neural_models.get(name), sgd_model, tokenizer,
                    latency_texts, max_len=max_len,
                    warmup=latency_warmup, measured=latency_examples)
                model_metric_rows.append(metric)
            except Exception as e:
                failure_rows.append({
                    "run_id": run_id, "seed": int(seed), "model": name,
                    "chunk_step": num_chunks - 1, "stage": "model_metrics",
                    "error": str(e), "traceback": traceback.format_exc(),
                })
        checkpoint(f"completed seed={seed}")

    finished_at = utc_now()
    elapsed = time.time() - t0

    integrity = dataset_integrity(Path(data_dir))
    env = environment_info(Path(data_dir))
    source = source_revision(Path(__file__).resolve().parents[1])
    manifest = {
        "run_id": run_id,
        "protocol": "Sequential class-incremental streaming; train on arriving chunk only; test on all seen chunks",
        "command": command or " ".join([Path(sys.executable).name] + sys.argv),
        "argv": sys.argv,
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "elapsed_seconds": round(elapsed, 3),
        "dataset": {
            "name": dataset_name,
            "integrity": integrity,
            "splits": {"train": len(train_all), "val": len(val_all),
                       "test": len(test_all)},
            "test_usage": "evaluation only; never vocabulary/fitting/early-stopping/calibration-fitting/tuning",
        },
        "environment": env,
        "source": source,
        "config": {
            "seeds": [int(s) for s in seeds],
            "num_chunks": int(num_chunks),
            "chunk_seed": int(chunk_seed),
            "embed_dim": int(embed_dim),
            "hidden_size": int(hidden_size),
            "batch_size": int(batch_size),
            "lr": float(lr),
            "max_epochs": int(max_epochs),
            "patience": int(patience),
            "max_len": int(max_len),
            "sgd_epochs_per_chunk": int(sgd_epochs_per_chunk),
            "sgd_max_features": int(sgd_max_features),
            "calibration": {
                "enabled": bool(calibrate),
                "method": "temperature scaling fitted on current-chunk validation logits/log-probabilities; applied to test probabilities",
                "temperature_bounds": [1e-3, 200.0],
                "test_used_for_fit": False,
                "n_bins": int(n_bins),
            },
            "ci_method": "95% two-sided t CI across seeds: mean +/- t(0.975, df=n-1)*std/sqrt(n); requires >=2 seeds",
            "run_matrix": "model x seed x chunk_step x eval_chunk; eval_chunk <= chunk_step",
        },
        "models": {
            name: MODEL_SPECS[name] for name in selected_models
        },
        "chunking": {
            "intent_order": intent_order,
            "chunks": {str(c["chunk_id"]): c["labels"] for c in chunks},
        },
        "tokenizer": {
            "type": "SimpleTokenizer",
            "fit_on": "train split text only",
            "vocab_size": tokenizer.vocab_size,
            "max_len": int(max_len),
        },
        "results": {
            "raw_rows": len(raw_rows),
            "per_example_rows": len(per_example_rows),
            "learning_curve_rows": len(learning_rows),
            "model_metric_rows": len(model_metric_rows),
            "expected_cells": expected_cells,
            "completed_cells": len(raw_rows),
            "missing_cells": max(0, expected_cells - len(raw_rows)),
            "failures": len(failure_rows),
            "status": "completed" if len(raw_rows) == expected_cells and not failure_rows else "partial",
        },
        "notes": [
            "CfC ablations are the two documented ncps CfC variants: mode='pure' and mode='no_gate'.",
            "Neural heads grow with seen classes; TF-IDF+SGD uses a fixed full-label output space (documented baseline protocol).",
            "ECE/Brier are computed over each model's own output space; the SGD output space is the full 150-intent label set.",
            "Latency is single-example end-to-end CPU latency with tokenization/vectorization included.",
            "No claim is made that CfC is the winner; results are reported as observed.",
        ],
    }
    (run_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    checkpoint("finished", extra={"status": manifest["results"]["status"]})

    print(f"study done: {len(raw_rows)}/{expected_cells} raw cells -> {raw_path}")
    print(f"elapsed: {elapsed:.1f}s; failures: {len(failure_rows)}")
    return (raw_rows, per_example_rows, learning_rows, model_metric_rows,
            failure_rows, manifest)

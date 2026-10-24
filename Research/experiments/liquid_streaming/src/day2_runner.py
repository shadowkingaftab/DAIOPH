"""Day 2 common training interface for the liquid streaming study.

One ordered stream is fed to four models under identical conditions:

  * CfC, LSTM and GRU share the same train-only tokenizer, embedding size,
    hidden size, growing output-class set, chunk order and mini-batch
    boundaries.  The batches for an epoch are materialised ONCE and replayed
    for all three neural models.
  * TF-IDF + SGD uses ``partial_fit``.  It is initialised with the full label
    list and updated only on the examples that arrive in the current chunk.

Test data is used only for scoring after a chunk has been trained.  It is never
used for vocabulary, fitting, early stopping or tuning.  Validation is used for
neural early stopping only.
"""
from __future__ import annotations

import csv
import json
import os
import random
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn

from chunks import create_class_incremental_chunks
from data import load_intent_dataset
from models import (CfcTextClassifier, GRUTextClassifier, LSTMTextClassifier,
                    TfidfSgdClassifier)
from tokenizer import SimpleTokenizer

NEURAL_MODELS = ("cfc", "lstm", "gru")
ALL_MODELS = ("cfc", "lstm", "gru", "tfidf_sgd")
MODEL_CLASSES = {
    "cfc": CfcTextClassifier,
    "lstm": LSTMTextClassifier,
    "gru": GRUTextClassifier,
}


def set_global_seed(seed: int) -> None:
    """Fix Python, NumPy and PyTorch RNGs and request deterministic kernels."""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    try:
        torch.use_deterministic_algorithms(True, warn_only=True)
    except Exception:
        pass


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def _encode_pairs(pairs: Sequence[Tuple[str, str]], tokenizer: SimpleTokenizer,
                  label_to_idx: Dict[str, int], max_len: int) -> Tuple[torch.Tensor, torch.Tensor]:
    ids_list = []
    labels = []
    for text, label in pairs:
        ids = tokenizer.encode(text, max_len=max_len)
        if len(ids) < max_len:
            ids = ids + [tokenizer.pad_id] * (max_len - len(ids))
        else:
            ids = ids[:max_len]
        ids_list.append(ids)
        labels.append(label_to_idx[label])
    return (torch.tensor(ids_list, dtype=torch.long),
            torch.tensor(labels, dtype=torch.long))


def build_epoch_batches(pairs: Sequence[Tuple[str, str]], tokenizer: SimpleTokenizer,
                        label_to_idx: Dict[str, int], batch_size: int,
                        max_len: int, seed: int,
                        shuffle: bool = True) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    """Create one deterministic epoch of mini-batches.

    The returned list is reused unchanged by CfC, LSTM and GRU so their batch
    boundaries and example order are identical.
    """
    indices = list(range(len(pairs)))
    if shuffle:
        random.Random(seed).shuffle(indices)
    batches: List[Tuple[torch.Tensor, torch.Tensor]] = []
    for start in range(0, len(indices), batch_size):
        chunk_indices = indices[start:start + batch_size]
        batch_pairs = [pairs[i] for i in chunk_indices]
        batches.append(_encode_pairs(batch_pairs, tokenizer, label_to_idx, max_len))
    return batches


def evaluate_neural(model: nn.Module, batches: Sequence[Tuple[torch.Tensor, torch.Tensor]],
                    idx_to_label: Sequence[str]) -> Tuple[float, int, List[str]]:
    model.eval()
    correct = 0
    total = 0
    predictions: List[str] = []
    with torch.no_grad():
        for ids, y in batches:
            logits = model(ids)
            pred = logits.argmax(dim=1)
            correct += int((pred == y).sum().item())
            total += int(y.size(0))
            predictions.extend(idx_to_label[int(i)] for i in pred.tolist())
    return (correct / total if total else 0.0), total, predictions


def _select_pairs(pairs: Sequence[Tuple[str, str]], max_examples: Optional[int]
                  ) -> List[Tuple[str, str]]:
    if max_examples is None:
        return list(pairs)
    return list(pairs[: max(0, int(max_examples))])


def _train_neural_models_shared(models: Dict[str, nn.Module],
                                train_pairs: Sequence[Tuple[str, str]],
                                val_pairs: Sequence[Tuple[str, str]],
                                tokenizer: SimpleTokenizer,
                                label_to_idx: Dict[str, int],
                                cfg: Dict[str, Any], seed: int,
                                chunk_id: int) -> Dict[str, Dict[str, Any]]:
    """Train all neural models from identically materialised epoch batches."""
    criterion = nn.CrossEntropyLoss()
    optimizers = {name: torch.optim.Adam(model.parameters(), lr=cfg["lr"])
                  for name, model in models.items()}
    best_val = {name: float("-inf") for name in models}
    best_state: Dict[str, Optional[Dict[str, torch.Tensor]]] = {name: None for name in models}
    patience_left = {name: int(cfg["patience"]) for name in models}
    epochs_run = {name: 0 for name in models}
    param_updates = {name: 0 for name in models}
    examples_processed = {name: 0 for name in models}
    active = set(models)

    val_batches: List[Tuple[torch.Tensor, torch.Tensor]] = []
    idx_to_label = [None] * len(label_to_idx)
    for label, idx in label_to_idx.items():
        idx_to_label[idx] = label
    if val_pairs and cfg["patience"] is not None and cfg["patience"] > 0:
        val_batches = build_epoch_batches(
            val_pairs, tokenizer, label_to_idx, cfg["batch_size"],
            cfg["max_len"], seed=seed, shuffle=False)

    for epoch in range(int(cfg["max_epochs"])):
        if not active:
            break
        epoch_seed = seed * 1_000_000 + chunk_id * 10_000 + epoch
        batches = build_epoch_batches(
            train_pairs, tokenizer, label_to_idx, cfg["batch_size"],
            cfg["max_len"], seed=epoch_seed, shuffle=True)

        for name in list(active):
            model = models[name]
            optimizer = optimizers[name]
            model.train()
            for ids, y in batches:
                optimizer.zero_grad()
                loss = criterion(model(ids), y)
                loss.backward()
                optimizer.step()
                param_updates[name] += 1
                examples_processed[name] += int(y.size(0))
            epochs_run[name] += 1

            if val_batches and cfg["patience"] is not None and cfg["patience"] > 0:
                val_acc, _, _ = evaluate_neural(model, val_batches, idx_to_label)
                if val_acc > best_val[name]:
                    best_val[name] = val_acc
                    best_state[name] = {
                        k: v.detach().clone() for k, v in model.state_dict().items()
                    }
                    patience_left[name] = int(cfg["patience"])
                else:
                    patience_left[name] -= 1
                    if patience_left[name] <= 0:
                        active.discard(name)

    for name, state in best_state.items():
        if state is not None:
            models[name].load_state_dict(state)

    return {
        name: {
            "epochs_completed": epochs_run[name],
            "parameter_updates": param_updates[name],
            "examples_processed": examples_processed[name],
            "best_val_accuracy": (None if best_val[name] == float("-inf")
                                  else round(best_val[name], 6)),
        }
        for name in models
    }


def _write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_day2(data_dir: Path, run_dir: Path, seed: int = 0,
             num_chunks: int = 5, chunk_seed: int = 12345,
             max_chunks: Optional[int] = None,
             embed_dim: int = 64, hidden_size: int = 64,
             batch_size: int = 32, lr: float = 1e-3,
             max_epochs: int = 10, patience: int = 2, max_len: int = 64,
             sgd_epochs_per_chunk: int = 5, sgd_max_features: int = 50000,
             tokenizer_min_freq: int = 1, tokenizer_max_vocab: int = 20000,
             max_train_examples_per_chunk: Optional[int] = None,
             max_val_examples_per_chunk: Optional[int] = None,
             max_eval_examples_per_chunk: Optional[int] = None,
             save_predictions: bool = False) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    set_global_seed(seed)
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    ds = load_intent_dataset(Path(data_dir))
    dataset_name = ds["name"]
    train_all = ds["train"]
    val_all = ds["val"]
    test_all = ds["test"]

    tokenizer = SimpleTokenizer([t for t, _ in train_all],
                                min_freq=tokenizer_min_freq,
                                max_vocab_size=tokenizer_max_vocab)
    chunks, intent_order = create_class_incremental_chunks(
        train_all, num_chunks=num_chunks, seed=chunk_seed)

    full_label_list = sorted(set(label for _, label in train_all))
    intent_to_chunk: Dict[str, int] = {}
    for chunk in chunks:
        for label in chunk["labels"]:
            intent_to_chunk[label] = chunk["chunk_id"]

    def split_by_chunk(pairs: Iterable[Tuple[str, str]]) -> Dict[int, List[Tuple[str, str]]]:
        out: Dict[int, List[Tuple[str, str]]] = {i: [] for i in range(num_chunks)}
        for text, label in pairs:
            if label in intent_to_chunk:
                out[intent_to_chunk[label]].append((text, label))
        return out

    val_by_chunk = split_by_chunk(val_all)
    test_by_chunk = split_by_chunk(test_all)

    sgd = TfidfSgdClassifier(
        max_features=sgd_max_features, epochs_per_chunk=sgd_epochs_per_chunk,
        random_state=seed)
    sgd.fit_vectorizer([t for t, _ in train_all])
    sgd.initialize_classes(full_label_list)

    chunks_to_run = chunks[:max_chunks] if max_chunks is not None else chunks
    rows: List[Dict[str, Any]] = []
    prediction_rows: List[Dict[str, Any]] = []
    update_budget: Dict[str, Dict[str, Any]] = {
        name: {"chunks": [], "total_parameter_updates": 0,
               "total_examples_processed": 0, "total_epochs_completed": 0}
        for name in ALL_MODELS
    }

    seed_before_models = random.getstate()
    initial_num_classes = (len(chunks_to_run[0]["labels"]) if chunks_to_run else 0)
    neural_models: Dict[str, nn.Module] = {}
    for name in NEURAL_MODELS:
        set_global_seed(seed)
        neural_models[name] = MODEL_CLASSES[name](
            vocab_size=tokenizer.vocab_size, embed_dim=embed_dim,
            hidden_size=hidden_size, num_classes=initial_num_classes,
            pad_id=tokenizer.pad_id)
    random.setstate(seed_before_models)

    classes_seen: List[str] = []
    for chunk in chunks_to_run:
        chunk_id = int(chunk["chunk_id"])
        chunk_labels = sorted(chunk["labels"])
        classes_seen = sorted(set(classes_seen) | set(chunk_labels))
        label_to_idx = {label: i for i, label in enumerate(classes_seen)}
        idx_to_label = classes_seen

        train_pairs = _select_pairs(chunk["train"], max_train_examples_per_chunk)
        val_pairs = [(t, l) for t, l in _select_pairs(
            val_by_chunk[chunk_id], max_val_examples_per_chunk) if l in label_to_idx]

        n_classes = len(classes_seen)
        for name in NEURAL_MODELS:
            neural_models[name].set_num_classes(n_classes)

        if train_pairs:
            neural_budget = _train_neural_models_shared(
                neural_models, train_pairs, val_pairs, tokenizer, label_to_idx,
                cfg={"lr": lr, "max_epochs": max_epochs, "patience": patience,
                     "batch_size": batch_size, "max_len": max_len},
                seed=seed, chunk_id=chunk_id)
        else:
            neural_budget = {
                name: {"epochs_completed": 0, "parameter_updates": 0,
                       "examples_processed": 0, "best_val_accuracy": None}
                for name in NEURAL_MODELS
            }
        for name in NEURAL_MODELS:
            entry = neural_budget[name]
            budget = update_budget[name]
            budget["chunks"].append({"chunk_step": chunk_id,
                                     "n_train_examples": len(train_pairs), **entry})
            budget["total_parameter_updates"] += entry["parameter_updates"]
            budget["total_examples_processed"] += entry["examples_processed"]
            budget["total_epochs_completed"] += entry["epochs_completed"]

        # Online TF-IDF + SGD: full label list fixed; update on this chunk only.
        text_labels = [(t, l) for t, l in train_pairs]
        updates_before = sgd.partial_fit_calls
        if text_labels:
            sgd.partial_fit([t for t, _ in text_labels],
                            [l for _, l in text_labels],
                            classes=full_label_list)
        chunk_updates = sgd.partial_fit_calls - updates_before
        sgd_chunk = {
            "chunk_step": chunk_id,
            "n_train_examples": len(text_labels),
            "epochs_completed": sgd_epochs_per_chunk if text_labels else 0,
            "parameter_updates": chunk_updates,
            "examples_processed": len(text_labels) * (sgd_epochs_per_chunk if text_labels else 0),
            "best_val_accuracy": None,
        }
        sgd_budget = update_budget["tfidf_sgd"]
        sgd_budget["chunks"].append(sgd_chunk)
        sgd_budget["total_parameter_updates"] += chunk_updates
        sgd_budget["total_examples_processed"] += sgd_chunk["examples_processed"]
        sgd_budget["total_epochs_completed"] += sgd_chunk["epochs_completed"]

        for eval_chunk_id in range(chunk_id + 1):
            eval_pairs = [(t, l) for t, l in _select_pairs(
                test_by_chunk[eval_chunk_id], max_eval_examples_per_chunk)
                if l in label_to_idx]
            eval_batches = build_epoch_batches(
                eval_pairs, tokenizer, label_to_idx, batch_size, max_len,
                seed=seed, shuffle=False)

            for name in NEURAL_MODELS:
                acc, n_eval, predictions = evaluate_neural(
                    neural_models[name], eval_batches, idx_to_label)
                rows.append({
                    "seed": seed, "model": name, "chunk_step": chunk_id,
                    "eval_chunk": eval_chunk_id, "accuracy": round(acc, 6),
                    "n_classes_seen": n_classes,
                    "n_train_examples": len(train_pairs),
                    "n_eval_examples": n_eval,
                    "n_predictions": len(predictions),
                })
                if save_predictions:
                    for pos, ((text, true_label), pred_label) in enumerate(
                            zip(eval_pairs, predictions)):
                        prediction_rows.append({
                            "seed": seed, "model": name, "chunk_step": chunk_id,
                            "eval_chunk": eval_chunk_id, "example_index": pos,
                            "text": text, "true_label": true_label,
                            "predicted_label": pred_label,
                            "correct": int(pred_label == true_label),
                        })

            if eval_pairs:
                sgd_predictions = sgd.predict([t for t, _ in eval_pairs]).tolist()
            else:
                sgd_predictions = []
            correct = sum(int(p == l) for p, (_, l) in zip(sgd_predictions, eval_pairs))
            acc = correct / len(eval_pairs) if eval_pairs else 0.0
            rows.append({
                "seed": seed, "model": "tfidf_sgd", "chunk_step": chunk_id,
                "eval_chunk": eval_chunk_id, "accuracy": round(acc, 6),
                "n_classes_seen": n_classes,
                "n_train_examples": len(train_pairs),
                "n_eval_examples": len(eval_pairs),
                "n_predictions": len(sgd_predictions),
            })
            if save_predictions:
                for pos, ((text, true_label), pred_label) in enumerate(
                        zip(eval_pairs, sgd_predictions)):
                    prediction_rows.append({
                        "seed": seed, "model": "tfidf_sgd", "chunk_step": chunk_id,
                        "eval_chunk": eval_chunk_id, "example_index": pos,
                        "text": text, "true_label": true_label,
                        "predicted_label": pred_label,
                        "correct": int(pred_label == true_label),
                    })

    fields = ["seed", "model", "chunk_step", "eval_chunk", "accuracy",
              "n_classes_seen", "n_train_examples", "n_eval_examples",
              "n_predictions"]
    _write_csv(run_dir / "raw_results.csv", rows, fields)
    if save_predictions:
        _write_csv(run_dir / "predictions.csv", prediction_rows,
                   ["seed", "model", "chunk_step", "eval_chunk", "example_index",
                    "text", "true_label", "predicted_label", "correct"])

    run_id = time.strftime("%Y%m%d-%H%M%S")
    manifest: Dict[str, Any] = {
        "run_id": run_id,
        "protocol": "Day 2 common streaming runner",
        "seed": seed,
        "seeds": {
            "python_random": seed,
            "numpy": seed,
            "torch": seed,
            "torch_cuda": seed,
            "chunk_order": chunk_seed,
            "model_init": seed,
            "batch_shuffle_formula": "seed*1_000_000 + chunk_step*10_000 + epoch",
            "pythonhashseed": str(seed),
        },
        "deterministic": {
            "cudnn_deterministic": bool(torch.backends.cudnn.deterministic),
            "cudnn_benchmark": bool(torch.backends.cudnn.benchmark),
            "torch_use_deterministic_algorithms": "requested (warn_only=True)",
        },
        "environment": {
            "python": os.sys.version.split()[0],
            "numpy": _package_version("numpy"),
            "torch": _package_version("torch"),
            "scikit-learn": _package_version("scikit-learn"),
            "ncps": _package_version("ncps"),
        },
        "dataset": {
            "name": dataset_name,
            "splits": {"train": len(train_all), "val": len(val_all),
                       "test": len(test_all)},
            "test_usage": "evaluation only; never vocabulary/fitting/early-stopping/tuning",
        },
        "tokenizer": {
            "type": "SimpleTokenizer",
            "fit_on": "train split text only",
            "min_freq": tokenizer_min_freq,
            "max_vocab_size": tokenizer_max_vocab,
            "vocab_size": tokenizer.vocab_size,
            "max_len": max_len,
            "pad_id": tokenizer.pad_id,
            "unk_id": tokenizer.unk_id,
        },
        "chunking": {
            "num_chunks": num_chunks,
            "chunks_used": len(chunks_to_run),
            "chunk_seed": chunk_seed,
            "intent_order": intent_order,
            "chunks": {str(c["chunk_id"]): c["labels"] for c in chunks},
        },
        "stream": {
            "chunk_steps_used": [int(c["chunk_id"]) for c in chunks_to_run],
            "train_examples_per_chunk_used": max_train_examples_per_chunk,
            "val_examples_per_chunk_used": max_val_examples_per_chunk,
            "eval_examples_per_chunk_used": max_eval_examples_per_chunk,
            "full_label_list": full_label_list,
            "n_full_labels": len(full_label_list),
        },
        "model_settings": {
            "neural_common": {
                "models": list(NEURAL_MODELS),
                "vocab_size": tokenizer.vocab_size,
                "embed_dim": embed_dim,
                "hidden_size": hidden_size,
                "num_classes": "grows with chunks; identical for cfc/lstm/gru",
                "max_len": max_len,
                "batch_size": batch_size,
                "shared_batch_boundaries": True,
                "batch_order_shuffle": True,
                "optimizer": "Adam",
                "lr": lr,
                "loss": "CrossEntropyLoss",
                "max_epochs_per_chunk": max_epochs,
                "early_stopping": {
                    "enabled": bool(patience is not None and patience > 0),
                    "metric": "validation accuracy on current chunk",
                    "patience": patience,
                    "uses_test_data": False,
                },
            },
            "cfc": {
                "architecture": "Embedding -> ncps CfC -> Linear",
                "cfc_input_size": embed_dim,
                "cfc_units": hidden_size,
                "return_sequences": False,
                "batch_first": True,
            },
            "lstm": {
                "architecture": "Embedding -> LSTM -> Linear",
                "input_size": embed_dim,
                "hidden_size": hidden_size,
                "num_layers": 1,
                "batch_first": True,
            },
            "gru": {
                "architecture": "Embedding -> GRU -> Linear",
                "input_size": embed_dim,
                "hidden_size": hidden_size,
                "num_layers": 1,
                "batch_first": True,
            },
            "tfidf_sgd": {
                "architecture": "TfidfVectorizer -> SGDClassifier(partial_fit)",
                "vectorizer_fit_on": "train split text only (all chunks; never test)",
                "max_features": sgd_max_features,
                "ngram_range": [1, 2],
                "loss": "log_loss",
                "learning_rate": "optimal",
                "random_state": seed,
                "classes_initialized_with": "full label list",
                "n_initial_classes": len(full_label_list),
                "epochs_per_chunk": sgd_epochs_per_chunk,
                "trained_on": "only examples in the current stream chunk",
            },
        },
        "update_budget": update_budget,
        "results": {
            "raw_rows": len(rows),
            "prediction_rows": len(prediction_rows),
            "models": list(ALL_MODELS),
            "models_with_predictions": sorted(
                {r["model"] for r in rows if r["n_predictions"] > 0}),
        },
        "elapsed_seconds": round(time.time() - t0, 3),
    }
    (run_dir / "run_metadata.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    return rows, prediction_rows, manifest

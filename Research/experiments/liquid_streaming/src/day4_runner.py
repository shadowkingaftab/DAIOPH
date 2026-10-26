"""Day 4 CfC ablations + calibration runner."""
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
from models import CfcTextClassifier
from tokenizer import SimpleTokenizer
from calibration import fit_temperature, apply_temperature, compute_ece, softmax
from day2_runner import (set_global_seed, build_epoch_batches, _select_pairs,
                         _train_neural_models_shared, _package_version)

ABLATION_MODELS = ("cfc_h32", "cfc_h64", "cfc_mm_on", "cfc_mm_off")

MODEL_CONFIG = {
    "cfc_h32": {"hidden_size": 32, "mixed_memory": False,
                "ablation": "hidden_size", "level": "32"},
    "cfc_h64": {"hidden_size": 64, "mixed_memory": False,
                "ablation": "hidden_size", "level": "64"},
    "cfc_mm_on": {"hidden_size": 64, "mixed_memory": True,
                  "ablation": "mixed_memory", "level": "on"},
    "cfc_mm_off": {"hidden_size": 64, "mixed_memory": False,
                   "ablation": "mixed_memory", "level": "off"},
}


def _write_csv(path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _collect_logits(model, batches):
    model.eval()
    logits_list = []
    labels_list = []
    preds_list = []
    correct = 0
    total = 0
    with torch.no_grad():
        for ids, y in batches:
            logits = model(ids)
            pred = logits.argmax(dim=1)
            correct += int((pred == y).sum().item())
            total += int(y.size(0))
            logits_list.append(logits.cpu().numpy())
            labels_list.append(y.cpu().numpy())
            preds_list.extend(int(i) for i in pred.tolist())
    if logits_list:
        logits_arr = np.concatenate(logits_list, axis=0)
        labels_arr = np.concatenate(labels_list, axis=0)
    else:
        logits_arr = np.zeros((0, 0))
        labels_arr = np.array([], dtype=int)
    acc = (correct / total if total else 0.0)
    return acc, total, preds_list, logits_arr, labels_arr

def run_day4(data_dir, run_dir, seed=0,
             num_chunks=5, chunk_seed=12345,
             max_chunks=None,
             embed_dim=64,
             batch_size=32, lr=1e-3,
             max_epochs=10, patience=2, max_len=64,
             tokenizer_min_freq=1, tokenizer_max_vocab=20000,
             max_train_examples_per_chunk=None,
             max_val_examples_per_chunk=None,
             max_eval_examples_per_chunk=None,
             save_predictions=True,
             calibrate=True):
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
    intent_to_chunk = {}
    for chunk in chunks:
        for label in chunk["labels"]:
            intent_to_chunk[label] = chunk["chunk_id"]

    def split_by_chunk(pairs):
        out = {i: [] for i in range(num_chunks)}
        for text, label in pairs:
            if label in intent_to_chunk:
                out[intent_to_chunk[label]].append((text, label))
        return out

    val_by_chunk = split_by_chunk(val_all)
    test_by_chunk = split_by_chunk(test_all)

    chunks_to_run = chunks[:max_chunks] if max_chunks is not None else chunks

    rows = []
    prediction_rows = []
    calibration_rows = []
    reliability_rows = []

    update_budget = {name: {"chunks": [], "total_parameter_updates": 0,
                           "total_examples_processed": 0, "total_epochs_completed": 0}
                     for name in ABLATION_MODELS}

    seed_before_models = random.getstate()
    initial_num_classes = (len(chunks_to_run[0]["labels"]) if chunks_to_run else 0)
    neural_models = {}
    for name in ABLATION_MODELS:
        set_global_seed(seed)
        cfgm = MODEL_CONFIG[name]
        neural_models[name] = CfcTextClassifier(
            vocab_size=tokenizer.vocab_size, embed_dim=embed_dim,
            hidden_size=cfgm["hidden_size"], num_classes=initial_num_classes,
            pad_id=tokenizer.pad_id, mixed_memory=cfgm["mixed_memory"])
    random.setstate(seed_before_models)

    classes_seen = []
    for chunk in chunks_to_run:
        chunk_id = int(chunk["chunk_id"])
        chunk_labels = sorted(chunk["labels"])
        classes_seen = sorted(set(classes_seen) | set(chunk_labels))
        n_classes = len(classes_seen)
        label_to_idx = {lab: i for i, lab in enumerate(classes_seen)}
        idx_to_label = [None] * n_classes
        for lab, idx in label_to_idx.items():
            idx_to_label[idx] = lab

        train_pairs = _select_pairs(chunk["train"], max_train_examples_per_chunk)
        val_pairs = _select_pairs(val_by_chunk[chunk_id], max_val_examples_per_chunk)

        cfg = {"batch_size": batch_size, "lr": lr, "max_epochs": max_epochs,
               "patience": patience, "max_len": max_len}

        for name in ABLATION_MODELS:
            neural_models[name].set_num_classes(n_classes)

        budget_info = _train_neural_models_shared(
            neural_models, train_pairs, val_pairs, tokenizer, label_to_idx,
            cfg, seed, chunk_id)

        temperatures = {}
        for name in ABLATION_MODELS:
            model = neural_models[name]
            temperature = 1.0
            if calibrate and val_pairs:
                val_batches = build_epoch_batches(
                    val_pairs, tokenizer, label_to_idx, batch_size, max_len,
                    seed=seed, shuffle=False)
                _, _, _, val_logits, val_labels = _collect_logits(model, val_batches)
                if val_logits.size > 0:
                    temperature = fit_temperature(val_logits, val_labels)
            temperatures[name] = float(temperature)
        for name in ABLATION_MODELS:
            model = neural_models[name]
            temperature = temperatures[name]
            for eval_chunk_id in range(chunk_id + 1):
                eval_pairs_full = test_by_chunk[eval_chunk_id]
                eval_pairs = _select_pairs(eval_pairs_full, max_eval_examples_per_chunk)
                test_batches = build_epoch_batches(
                    eval_pairs, tokenizer, label_to_idx, batch_size, max_len,
                    seed=seed, shuffle=False) if eval_pairs else []

                acc, n, preds, test_logits, test_labels = _collect_logits(model, test_batches)

                if test_logits.size > 0:
                    uncal_probs = softmax(test_logits, axis=1)
                    cal_probs = (apply_temperature(test_logits, temperature)
                                 if calibrate else uncal_probs)
                else:
                    uncal_probs = np.zeros((0, n_classes))
                    cal_probs = uncal_probs

                if save_predictions:
                    for pos in range(len(eval_pairs)):
                        text, true_label_str = eval_pairs[pos]
                        true_idx = label_to_idx[true_label_str]
                        pred_idx = int(preds[pos]) if pos < len(preds) else 0
                        logit_vec = (test_logits[pos] if test_logits.size > 0 and pos < len(test_logits)
                                     else np.zeros(n_classes))
                        u_p = (uncal_probs[pos] if uncal_probs.size > 0 and pos < len(uncal_probs)
                               else np.zeros(n_classes))
                        c_p = (cal_probs[pos] if cal_probs.size > 0 and pos < len(cal_probs)
                               else np.zeros(n_classes))
                        prediction_rows.append({
                            "seed": seed, "model": name,
                            "ablation": MODEL_CONFIG[name]["ablation"],
                            "variant": MODEL_CONFIG[name]["level"],
                            "hidden_size": MODEL_CONFIG[name]["hidden_size"],
                            "mixed_memory": MODEL_CONFIG[name]["mixed_memory"],
                            "chunk_step": chunk_id, "eval_chunk": eval_chunk_id,
                            "example_index": pos, "text": text,
                            "true_label": true_label_str,
                            "true_label_idx": int(true_idx),
                            "predicted_label": idx_to_label[pred_idx],
                            "predicted_label_idx": int(pred_idx),
                            "correct": int(pred_idx == true_idx),
                            "prob_true_uncal": float(u_p[true_idx]),
                            "max_prob_uncal": float(u_p.max()) if u_p.size else 0.0,
                            "prob_true_cal": float(c_p[true_idx]),
                            "max_prob_cal": float(c_p.max()) if c_p.size else 0.0,
                            "temperature": float(temperature),
                            "logits": [float(v) for v in logit_vec],
                        })

                if test_logits.size > 0:
                    ece_uncal = compute_ece(uncal_probs, test_labels.astype(int))
                    ece_cal = compute_ece(cal_probs, test_labels.astype(int))
                    calibration_rows.append({
                        "seed": seed, "model": name,
                        "ablation": MODEL_CONFIG[name]["ablation"],
                        "variant": MODEL_CONFIG[name]["level"],
                        "hidden_size": MODEL_CONFIG[name]["hidden_size"],
                        "mixed_memory": MODEL_CONFIG[name]["mixed_memory"],
                        "chunk_step": chunk_id, "eval_chunk": eval_chunk_id,
                        "n_examples": int(len(test_labels)),
                        "temperature": float(temperature),
                        "ece_uncalibrated": float(ece_uncal["ece"]),
                        "brier_uncalibrated": float(ece_uncal["brier"]),
                        "ece_calibrated": float(ece_cal["ece"]),
                        "brier_calibrated": float(ece_cal["brier"]),
                    })
                    for calibrated_flag, res in ((False, ece_uncal), (True, ece_cal)):
                        for b in res["bins"]:
                            reliability_rows.append({
                                "seed": seed, "model": name,
                                "ablation": MODEL_CONFIG[name]["ablation"],
                                "variant": MODEL_CONFIG[name]["level"],
                                "chunk_step": chunk_id, "eval_chunk": eval_chunk_id,
                                "calibrated": bool(calibrated_flag),
                                "bin_lower": float(b["bin_lower"]),
                                "bin_upper": float(b["bin_upper"]),
                                "count": int(b["count"]),
                                "accuracy": float(b["accuracy"]),
                                "avg_confidence": float(b["avg_confidence"]),
                                "gap": float(b["gap"]),
                            })

                rows.append({
                    "seed": seed, "model": name,
                    "ablation": MODEL_CONFIG[name]["ablation"],
                    "variant": MODEL_CONFIG[name]["level"],
                    "hidden_size": MODEL_CONFIG[name]["hidden_size"],
                    "mixed_memory": MODEL_CONFIG[name]["mixed_memory"],
                    "chunk_step": chunk_id, "eval_chunk": eval_chunk_id,
                    "accuracy": float(acc),
                    "n_classes_seen": n_classes,
                    "n_train_examples": len(train_pairs),
                    "n_eval_examples": n,
                    "n_predictions": len(eval_pairs),
                    "temperature": float(temperature),
                })

            update_budget[name]["chunks"].append({
                "chunk_step": chunk_id,
                "epochs_completed": budget_info[name]["epochs_completed"],
                "parameter_updates": budget_info[name]["parameter_updates"],
                "examples_processed": budget_info[name]["examples_processed"],
                "best_val_accuracy": budget_info[name]["best_val_accuracy"],
                "temperature": temperatures[name],
            })
            update_budget[name]["total_parameter_updates"] += budget_info[name]["parameter_updates"]
            update_budget[name]["total_examples_processed"] += budget_info[name]["examples_processed"]
            update_budget[name]["total_epochs_completed"] += budget_info[name]["epochs_completed"]

    raw_fields = ["seed", "model", "ablation", "variant", "hidden_size", "mixed_memory",
                  "chunk_step", "eval_chunk", "accuracy", "n_classes_seen",
                  "n_train_examples", "n_eval_examples", "n_predictions", "temperature"]
    _write_csv(run_dir / "raw_results.csv", rows, raw_fields)

    if save_predictions:
        pred_fields = ["seed", "model", "ablation", "variant", "hidden_size", "mixed_memory",
                       "chunk_step", "eval_chunk", "example_index", "text",
                       "true_label", "true_label_idx", "predicted_label",
                       "predicted_label_idx", "correct", "prob_true_uncal",
                       "max_prob_uncal", "prob_true_cal", "max_prob_cal",
                       "temperature", "logits"]
        _write_csv(run_dir / "predictions.csv", prediction_rows, pred_fields)

    cal_fields = ["seed", "model", "ablation", "variant", "hidden_size", "mixed_memory",
                  "chunk_step", "eval_chunk", "n_examples", "temperature",
                  "ece_uncalibrated", "brier_uncalibrated",
                  "ece_calibrated", "brier_calibrated"]
    _write_csv(run_dir / "calibration_results.csv", calibration_rows, cal_fields)

    bin_fields = ["seed", "model", "ablation", "variant", "chunk_step", "eval_chunk",
                  "calibrated", "bin_lower", "bin_upper", "count", "accuracy",
                  "avg_confidence", "gap"]
    _write_csv(run_dir / "reliability_bins.csv", reliability_rows, bin_fields)
    run_id = time.strftime("%Y%m%d-%H%M%S")
    manifest = {
        "run_id": run_id,
        "protocol": "Day 4 CfC ablations + calibration",
        "seed": seed,
        "environment": {
            "python": os.sys.version.split()[0],
            "numpy": _package_version("numpy"),
            "torch": _package_version("torch"),
            "scikit-learn": _package_version("scikit-learn"),
            "ncps": _package_version("ncps"),
        },
        "dataset": {"name": dataset_name,
                    "splits": {"train": len(train_all), "val": len(val_all),
                               "test": len(test_all)}},
        "tokenizer": {"type": "SimpleTokenizer", "fit_on": "train split text only",
                      "vocab_size": tokenizer.vocab_size, "max_len": max_len,
                      "pad_id": tokenizer.pad_id},
        "chunking": {"num_chunks": num_chunks, "chunks_used": len(chunks_to_run),
                     "chunk_seed": chunk_seed, "intent_order": intent_order},
        "ablations": {
            "hidden_size": {"variants": ["cfc_h32", "cfc_h64"],
                            "description": "CfC hidden size 32 vs 64"},
            "mixed_memory": {"variants": ["cfc_mm_on", "cfc_mm_off"],
                             "description": "ncps CfC mixed_memory on vs off",
                             "supported": True,
                             "note": "ncps 0.0.2 CfC accepts mixed_memory; used directly."},
        },
        "calibration": {
            "method": "temperature_scaling",
            "fit_on": "validation split of current chunk only",
            "applied_to": "test logits",
            "uses_test_data_for_fitting": False,
            "ece_bins": 15,
        },
        "update_budget": update_budget,
        "results": {"raw_rows": len(rows),
                    "prediction_rows": len(prediction_rows),
                    "calibration_rows": len(calibration_rows),
                    "reliability_bin_rows": len(reliability_rows)},
        "elapsed_seconds": round(time.time() - t0, 3),
    }
    (run_dir / "run_metadata.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    return rows, prediction_rows, calibration_rows, reliability_rows, manifest

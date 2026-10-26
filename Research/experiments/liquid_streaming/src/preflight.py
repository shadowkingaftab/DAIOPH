"""Preflight check: disk, environment, dataset integrity, runtime estimate.

Usage:
    .venv\\Scripts\\python.exe src\\preflight.py --seeds 0,1,2 --max-epochs 10

Runs one measured epoch per model on chunk 0 (full-size training slice) and
extrapolates a conservative runtime range for the planned matrix.  It does not
modify any study outputs except the JSON report path.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))

from chunks import create_class_incremental_chunks  # noqa: E402
from data import load_intent_dataset  # noqa: E402
from models import TfidfSgdClassifier  # noqa: E402
from study_utils import (dataset_integrity, environment_info,  # noqa: E402
                         utc_now)
from tokenizer import SimpleTokenizer  # noqa: E402
from train_eval import (ALL_MODEL_NAMES, MODEL_SPECS, build_neural_model,  # noqa: E402
                        eval_sgd_simple, train_chunk_nn)


def _benchmark(data_dir: Path, max_len: int, batch_size: int,
               sgd_epochs: int) -> dict:
    ds = load_intent_dataset(data_dir)
    tokenizer = SimpleTokenizer([t for t, _ in ds["train"]], min_freq=1)
    chunks, _ = create_class_incremental_chunks(ds["train"], 5, 12345)
    chunk = chunks[0]
    labels = sorted(chunk["labels"])
    label_to_idx = {lab: i for i, lab in enumerate(labels)}
    train_pairs = chunk["train"]
    val_pairs = [(t, l) for t, l in ds["val"] if l in label_to_idx]

    timings = {}
    for name in ALL_MODEL_NAMES:
        spec = MODEL_SPECS[name]
        t0 = time.perf_counter()
        if spec["family"] == "sgd":
            clf = TfidfSgdClassifier(epochs_per_chunk=sgd_epochs,
                                     max_features=50000)
            clf.fit_vectorizer([t for t, _ in ds["train"]])
            clf.initialize_classes(sorted(set(l for _, l in ds["train"])))
            texts = [t for t, _ in train_pairs]
            labs = [l for _, l in train_pairs]
            for _ in range(max(1, sgd_epochs)):
                clf.partial_fit(texts, labs)
            eval_sgd_simple(clf, val_pairs, label_to_idx)
        else:
            model = build_neural_model(name, tokenizer.vocab_size, 64, 64,
                                       tokenizer.pad_id)
            model.set_num_classes(len(labels))
            train_chunk_nn(model, train_pairs, val_pairs, tokenizer, label_to_idx,
                           epochs=1, lr=1e-3, batch_size=batch_size, patience=99,
                           max_len=max_len, seed=0)
        timings[name] = round(time.perf_counter() - t0, 3)
        print(f"benchmark {name}: {timings[name]:.2f}s (1 epoch/chunk)", flush=True)
    return timings


def main() -> int:
    ap = argparse.ArgumentParser(description="Preflight for liquid streaming study")
    ap.add_argument("--data-dir", default=str(ROOT / "data"))
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--num-chunks", type=int, default=5)
    ap.add_argument("--max-epochs", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=64)
    ap.add_argument("--sgd-epochs-per-chunk", type=int, default=5)
    ap.add_argument("--out", default=str(ROOT / "outputs" / "preflight.json"))
    ap.add_argument("--no-benchmark", action="store_true")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    seeds = [int(s) for s in args.seeds.split(",")]
    env = environment_info(data_dir)
    integrity = dataset_integrity(data_dir)

    report = {
        "checked_at_utc": utc_now(),
        "environment": env,
        "dataset_integrity": integrity,
        "plan": {
            "seeds": seeds,
            "num_chunks": args.num_chunks,
            "max_epochs": args.max_epochs,
            "models": list(ALL_MODEL_NAMES),
        },
    }

    print("=== Environment ===")
    print(f"python: {env.get('python', '').splitlines()[0]}")
    print(f"packages: {env.get('packages')}")
    print(f"cpu_count: {env.get('cpu_count')}  cuda: {env.get('cuda_available')}")
    print(f"disk free: {env.get('disk', {}).get('free_gb')} GB")
    print("=== Dataset ===")
    print(f"ok: {integrity.get('ok')}")
    print(f"sha256: {integrity.get('actual_sha256')}")
    print(f"expected: {integrity.get('expected_sha256')}")

    if not integrity.get("ok"):
        report["ok"] = False
        report["error"] = "dataset integrity check failed"
    else:
        report["ok"] = True

    if not args.no_benchmark:
        timings = _benchmark(data_dir, args.max_len, args.batch_size,
                             args.sgd_epochs_per_chunk)
        # Early stopping usually finishes before max_epochs.  Report a range:
        # optimistic = 3 epochs/chunk, conservative = max_epochs/chunk.
        seed_factor = len(seeds)
        chunk_factor = args.num_chunks
        optimistic = sum(t * min(3, args.max_epochs) * chunk_factor * seed_factor
                         for t in timings.values())
        conservative = sum(t * args.max_epochs * chunk_factor * seed_factor
                           for t in timings.values())
        overhead = 1.25  # evaluation, calibration, model metrics, I/O
        report["benchmark"] = {
            "seconds_per_one_epoch_on_chunk0": timings,
            "note": "chunk0 full-size training slice; one epoch includes one validation pass",
            "estimated_seconds_optimistic_3_epochs": round(optimistic * overhead, 1),
            "estimated_seconds_conservative_max_epochs": round(conservative * overhead, 1),
            "estimated_minutes_optimistic": round(optimistic * overhead / 60, 1),
            "estimated_minutes_conservative": round(conservative * overhead / 60, 1),
            "overhead_factor": overhead,
        }
        n_examples_per_cell = 900
        per_example_rows = (len(ALL_MODEL_NAMES) * len(seeds) *
                            sum(range(1, args.num_chunks + 1)) * n_examples_per_cell)
        # Rough CSV size: ~180 bytes/row.
        report["estimated_outputs"] = {
            "per_example_rows": per_example_rows,
            "per_example_csv_mb_approx": round(per_example_rows * 180 / 1e6, 1),
        }
        print("=== Runtime estimate ===")
        print(f"optimistic (3 epochs/chunk): {report['benchmark']['estimated_minutes_optimistic']} min")
        print(f"conservative (max {args.max_epochs} epochs/chunk): "
              f"{report['benchmark']['estimated_minutes_conservative']} min")
        print(f"estimated per-example rows: {per_example_rows} "
              f"(~{report['estimated_outputs']['per_example_csv_mb_approx']} MB)")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"preflight report: {out_path}")
    return 0 if report.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())

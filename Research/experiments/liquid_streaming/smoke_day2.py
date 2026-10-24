"""One-seed, first-chunk smoke comparison for the Day 2 models.

Usage (from Research/experiments/liquid_streaming/):
    .venv\\Scripts\\python.exe smoke_day2.py

This is intentionally short: one seed, chunk 0 only, a small training slice and
one pass.  It runs CfC, LSTM, GRU and TF-IDF+SGD through the same shared runner.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.day2_runner import run_day2  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Day 2 first-chunk smoke comparison")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=str(ROOT / "out_day2_smoke"))
    ap.add_argument("--train-per-chunk", type=int, default=64)
    ap.add_argument("--max-eval", type=int, default=200)
    ap.add_argument("--max-epochs", type=int, default=1)
    ap.add_argument("--patience", type=int, default=0)
    ap.add_argument("--sgd-epochs-per-chunk", type=int, default=1)
    args = ap.parse_args()

    rows, predictions, manifest = run_day2(
        data_dir=ROOT / "data",
        run_dir=Path(args.out),
        seed=args.seed,
        num_chunks=5,
        chunk_seed=12345,
        max_chunks=1,
        embed_dim=64,
        hidden_size=64,
        batch_size=32,
        lr=1e-3,
        max_epochs=args.max_epochs,
        patience=args.patience,
        max_len=64,
        sgd_epochs_per_chunk=args.sgd_epochs_per_chunk,
        sgd_max_features=50000,
        max_train_examples_per_chunk=args.train_per_chunk,
        max_eval_examples_per_chunk=args.max_eval,
        save_predictions=True,
    )

    print("\n=== Day 2 smoke rows (seed=%d, chunk 0 only) ===" % args.seed)
    for row in rows:
        print(
            f"{row['model']:>10}  eval_chunk={row['eval_chunk']}  "
            f"accuracy={row['accuracy']:.4f}  "
            f"n_train={row['n_train_examples']}  "
            f"n_eval={row['n_eval_examples']}  "
            f"n_predictions={row['n_predictions']}"
        )
    print("\n=== Update budget ===")
    for name, budget in manifest["update_budget"].items():
        print(
            f"{name:>10}  updates={budget['total_parameter_updates']}  "
            f"examples={budget['total_examples_processed']}  "
            f"epochs={budget['total_epochs_completed']}"
        )
    print(f"\nrows={len(rows)} predictions={len(predictions)}")
    print(f"outputs: {Path(args.out).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

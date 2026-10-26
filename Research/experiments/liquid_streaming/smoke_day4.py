"""Day 4 smoke: CfC ablations + calibration on chunk 0."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.day4_runner import run_day4  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Day 4 CfC ablation + calibration smoke")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=str(ROOT / "out_day4_smoke"))
    ap.add_argument("--train-per-chunk", type=int, default=64)
    ap.add_argument("--max-eval", type=int, default=200)
    ap.add_argument("--max-epochs", type=int, default=1)
    ap.add_argument("--patience", type=int, default=0)
    args = ap.parse_args()

    rows, predictions, calibration, bins, manifest = run_day4(
        data_dir=ROOT / "data",
        run_dir=Path(args.out),
        seed=args.seed,
        num_chunks=5,
        chunk_seed=12345,
        max_chunks=1,
        embed_dim=64,
        batch_size=32,
        lr=1e-3,
        max_epochs=args.max_epochs,
        patience=args.patience,
        max_len=64,
        max_train_examples_per_chunk=args.train_per_chunk,
        max_val_examples_per_chunk=max(16, args.train_per_chunk // 4),
        max_eval_examples_per_chunk=args.max_eval,
        save_predictions=True,
        calibrate=True,
    )

    print("\n=== Day 4 smoke rows ===")
    for row in rows:
        print(f"{row['model']:>10}  eval_chunk={row['eval_chunk']}  "
              f"acc={row['accuracy']:.4f}  n_train={row['n_train_examples']}  "
              f"n_eval={row['n_eval_examples']}  T={row['temperature']:.3f}")
    print("\n=== Calibration (chunk 0, eval chunk 0) ===")
    for c in calibration:
        print(f"{c['model']:>10}  ECE_uncal={c['ece_uncalibrated']:.4f}  "
              f"ECE_cal={c['ece_calibrated']:.4f}  "
              f"Brier_uncal={c['brier_uncalibrated']:.4f}  "
              f"Brier_cal={c['brier_calibrated']:.4f}")
    print(f"\nrows={len(rows)} predictions={len(predictions)} "
          f"calibration={len(calibration)} bins={len(bins)}")
    print(f"outputs: {Path(args.out).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

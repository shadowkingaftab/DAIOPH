"""Reproducible entry point for the liquid streaming study.

Usage (from the study folder, using the project-local venv):
    .venv\\Scripts\\python.exe src\\run_study.py

Writes:
  outputs/runs/<run_id>/raw_results.csv
  outputs/runs/<run_id>/run_manifest.json
  outputs/aggregated/<run_id>_summary.csv     (mean +/- std across seeds)
  outputs/figures/*.png                       (accuracy vs chunk step per model)
"""
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]          # liquid_streaming/
DEFAULT_DATA = ROOT / "data"
DEFAULT_OUT = ROOT / "outputs"


def load_dataset_manifest(data_dir: Path) -> dict:
    m = data_dir / "dataset_manifest.json"
    if m.exists():
        return json.loads(m.read_text(encoding="utf-8"))
    return {}


def main():
    ap = argparse.ArgumentParser(description="Liquid streaming intent study")
    ap.add_argument("--data-dir", default=str(DEFAULT_DATA))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--seeds", default="0,1,2,3,4")
    ap.add_argument("--num-chunks", type=int, default=5)
    ap.add_argument("--chunk-seed", type=int, default=12345)
    ap.add_argument("--embed-dim", type=int, default=64)
    ap.add_argument("--hidden-size", type=int, default=64)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--max-epochs", type=int, default=10)
    ap.add_argument("--patience", type=int, default=2)
    ap.add_argument("--max-len", type=int, default=64)
    ap.add_argument("--sgd-epochs-per-chunk", type=int, default=5)
    ap.add_argument("--sgd-max-features", type=int, default=50000)
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out_root = Path(args.out)
    seeds = tuple(int(s) for s in args.seeds.split(","))

    run_dir = out_root / "runs" / time.strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)

    # Import study modules (they live next to this file)
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from train_eval import run_study

    rows, manifest = run_study(
        data_dir=data_dir, run_dir=run_dir, seeds=seeds,
        num_chunks=args.num_chunks, chunk_seed=args.chunk_seed,
        embed_dim=args.embed_dim, hidden_size=args.hidden_size,
        batch_size=args.batch_size, lr=args.lr, max_epochs=args.max_epochs,
        patience=args.patience, max_len=args.max_len,
        sgd_epochs_per_chunk=args.sgd_epochs_per_chunk,
        sgd_max_features=args.sgd_max_features,
    )

    # Attach dataset reproducibility metadata to the run manifest
    ds_manifest = load_dataset_manifest(data_dir)
    manifest["dataset_manifest"] = ds_manifest
    (run_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")

    # ---- aggregate across seeds ----
    df = pd.DataFrame(rows)
    agg_dir = out_root / "aggregated"
    agg_dir.mkdir(parents=True, exist_ok=True)
    summary = (
        df.groupby(["model", "chunk_step", "eval_chunk"])["accuracy"]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    summary_path = agg_dir / f"{manifest['run_id']}_summary.csv"
    summary.to_csv(summary_path, index=False)

    print("\n=== Aggregated accuracy (mean +/- std over seeds) ===")
    print(summary.round(4).to_string(index=False))
    print(f"\nRun dir: {run_dir}")
    print(f"Summary: {summary_path}")

    # ---- figures ----
    fig_dir = out_root / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    try:
        from plots import plot_accuracy_vs_chunk
        plot_accuracy_vs_chunk(df, fig_dir)
        print(f"Figures: {fig_dir}")
    except Exception as e:
        print(f"(plots skipped: {e})")


if __name__ == "__main__":
    main()

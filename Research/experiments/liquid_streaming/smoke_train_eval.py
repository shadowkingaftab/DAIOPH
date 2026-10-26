"""Smoke: train_eval run_study on 1 chunk, 1 seed, 1 epoch."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.train_eval import run_study  # noqa: E402


def main() -> int:
    rows, manifest = run_study(
        data_dir=ROOT / "data",
        run_dir=ROOT / "out_train_eval_smoke",
        seeds=(0,),
        num_chunks=1,
        chunk_seed=12345,
        embed_dim=64,
        hidden_size=64,
        batch_size=32,
        lr=1e-3,
        max_epochs=1,
        patience=0,
        max_len=64,
        sgd_epochs_per_chunk=1,
        sgd_max_features=50000,
        calibrate=True,
        save_per_example=True,
    )
    print(f"rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

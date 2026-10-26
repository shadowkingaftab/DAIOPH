"""Reproducible entry point for the complete liquid streaming study.

Usage (from the study folder, using the project-local venv):
    .venv\\Scripts\\python.exe src\\run_study.py --seeds 0,1,2 --num-chunks 5

Writes:
  outputs/runs/<run_id>/raw_results.csv
  outputs/runs/<run_id>/per_example_predictions.csv
  outputs/runs/<run_id>/learning_curves.csv
  outputs/runs/<run_id>/model_metrics.csv
  outputs/runs/<run_id>/failures.csv
  outputs/runs/<run_id>/run_manifest.json
  outputs/runs/<run_id>/RUN_REPORT.md
  outputs/aggregated/<run_id>_summary.csv              (mean/std/95% t-CI across seeds)
  outputs/aggregated/<run_id>_model_metrics_summary.csv
  outputs/aggregated/<run_id>_run_matrix*.csv/json
  outputs/figures/<run_id>/*.png
  outputs/locks/<run_id>.json + .locked
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data"
DEFAULT_OUT = ROOT / "outputs"

sys.path.insert(0, str(ROOT / "src"))

from study_utils import (aggregate_model_metrics, aggregate_raw,  # noqa: E402
                         dataset_integrity, environment_info, lock_outputs,
                         source_revision, utc_now, write_run_matrix)
from train_eval import ALL_MODEL_NAMES  # noqa: E402


def _unique_run_dir(out_root: Path) -> tuple[str, Path]:
    base = time.strftime("%Y%m%d-%H%M%S")
    run_id = base
    candidate = out_root / "runs" / run_id
    i = 1
    while candidate.exists():
        run_id = f"{base}-{i}"
        candidate = out_root / "runs" / run_id
        i += 1
    candidate.mkdir(parents=True, exist_ok=True)
    return run_id, candidate


def _write_report(run_dir: Path, manifest: dict, summary: pd.DataFrame,
                  matrix_overall: dict, fig_dir: Path, figures: list,
                  agg_files: dict, lock_path: Path, command: str) -> Path:
    lines = [
        f"# Run {manifest['run_id']} - liquid streaming study",
        "",
        "This report is generated automatically from the locked run artefacts.",
        "It reports observed results only; it does not claim that any model wins.",
        "",
        "## Provenance",
        "",
        f"- Command: `{command}`",
        f"- Started (UTC): {manifest.get('started_at_utc')}",
        f"- Finished (UTC): {manifest.get('finished_at_utc')}",
        f"- Elapsed seconds: {manifest.get('elapsed_seconds')}",
        f"- Git HEAD: `{manifest.get('source', {}).get('git_head')}`",
        f"- Git status (porcelain): `{manifest.get('source', {}).get('git_status_porcelain', '').replace(chr(10), '; ')}`",
        f"- Dataset: {manifest.get('dataset', {}).get('name')}",
        f"- Dataset SHA-256: `{manifest.get('dataset', {}).get('integrity', {}).get('actual_sha256')}`",
        f"- Dataset integrity OK: {manifest.get('dataset', {}).get('integrity', {}).get('ok')}",
        f"- Python: {manifest.get('environment', {}).get('python', '').splitlines()[0]}",
        f"- Packages: {json.dumps(manifest.get('environment', {}).get('packages', {}))}",
        f"- Seeds: {manifest.get('config', {}).get('seeds')}",
        f"- Chunks: {manifest.get('config', {}).get('num_chunks')}",
        f"- Models: {list(manifest.get('models', {}).keys())}",
        f"- Calibration: {manifest.get('config', {}).get('calibration', {}).get('method')}",
        f"- CI method: {manifest.get('config', {}).get('ci_method')}",
        "",
        "## Run matrix",
        "",
        f"- Expected cells: {matrix_overall.get('expected_cells')}",
        f"- Completed cells: {matrix_overall.get('completed_cells')}",
        f"- Missing cells: {matrix_overall.get('missing_cells')}",
        f"- Status: **{matrix_overall.get('status')}**",
        f"- Matrix: `{agg_files.get('run_matrix')}`",
        f"- Matrix summary: `{agg_files.get('run_matrix_summary')}`",
        "",
        "## Final-step aggregate (mean +/- std over seeds)",
        "",
    ]
    if not summary.empty:
        final_step = int(summary["chunk_step"].max())
        cols = ["model", "chunk_step", "eval_chunk", "accuracy_mean",
                "accuracy_std", "accuracy_ci95_low", "accuracy_ci95_high",
                "ece_calibrated_mean", "brier_calibrated_mean"]
        cols = [c for c in cols if c in summary.columns]
        final = summary[summary["chunk_step"] == final_step][cols]
        lines.append("```")
        lines.append(final.round(4).to_string(index=False))
        lines.append("```")
    else:
        lines.append("_No completed cells._")
    lines += [
        "",
        "## Figures (regenerated from saved CSVs only)",
        "",
        f"- Figure directory: `{fig_dir}`",
    ]
    for f in figures:
        lines.append(f"- `{Path(f).name}`")
    lines += [
        "",
        "Reproduce figures without training:",
        "",
        "```powershell",
        f'.venv\\Scripts\\python.exe src\\plot_results.py --run-dir "{run_dir}" --out "{fig_dir}"',
        "```",
        "",
        "## Artefacts",
        "",
    ]
    for k, v in agg_files.items():
        lines.append(f"- {k}: `{v}`")
    lines += [
        "",
        "## Caveats",
        "",
        "- Neural heads grow with seen classes; TF-IDF+SGD uses a fixed full-label output space.",
        "- ECE/Brier are computed over each model's own output space.",
        "- Latency is single-example end-to-end CPU latency including tokenization/vectorization.",
        "- No replay, distillation or regularization is used; forgetting is expected in this protocol.",
        "- Figures are descriptive; no significance claim is made from three seeds.",
        "",
        f"Lock file: `{lock_path}`",
    ]
    path = run_dir / "RUN_REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main():
    ap = argparse.ArgumentParser(description="Complete liquid streaming study")
    ap.add_argument("--data-dir", default=str(DEFAULT_DATA))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--seeds", default="0,1,2")
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
    ap.add_argument("--calibrate", dest="calibrate", action="store_true", default=True)
    ap.add_argument("--no-calibrate", dest="calibrate", action="store_false")
    ap.add_argument("--no-per-example", dest="save_per_example", action="store_false", default=True)
    ap.add_argument("--n-bins", type=int, default=15)
    ap.add_argument("--latency-examples", type=int, default=100)
    ap.add_argument("--latency-warmup", type=int, default=5)
    ap.add_argument("--models", default=",".join(ALL_MODEL_NAMES),
                    help="comma-separated model names")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out_root = Path(args.out)
    seeds = tuple(int(s) for s in args.seeds.split(","))
    models = tuple(m.strip() for m in args.models.split(",") if m.strip())
    command = " ".join([str(Path(sys.executable))] + sys.argv)

    # ---- preflight: disk, environment, dataset integrity ----
    env = environment_info(data_dir)
    integrity = dataset_integrity(data_dir)
    free_gb = env.get("disk", {}).get("free_gb")
    print("=== Preflight ===")
    print(f"python: {env.get('python', '').splitlines()[0]}")
    print(f"packages: {env.get('packages')}")
    print(f"disk free: {free_gb} GB")
    print(f"dataset integrity ok: {integrity.get('ok')} "
          f"(sha256={integrity.get('actual_sha256')})")
    if not integrity.get("ok"):
        raise SystemExit("Dataset integrity check failed; refusing to run. "
                         "See data/dataset_manifest.json.")
    if free_gb is not None and free_gb < 1.0:
        raise SystemExit("Less than 1 GB free disk; refusing to start.")
    if not args.calibrate:
        print("NOTE: calibration disabled; calibration figures will be uncalibrated.")

    out_root.mkdir(parents=True, exist_ok=True)
    run_id, run_dir = _unique_run_dir(out_root)
    print(f"run_id: {run_id}")
    print(f"run_dir: {run_dir}")

    from train_eval import run_study as execute_study
    raw_rows, per_example_rows, learning_rows, model_metric_rows, failure_rows, manifest = execute_study(
        data_dir=data_dir, run_dir=run_dir, seeds=seeds,
        num_chunks=args.num_chunks, chunk_seed=args.chunk_seed,
        embed_dim=args.embed_dim, hidden_size=args.hidden_size,
        batch_size=args.batch_size, lr=args.lr, max_epochs=args.max_epochs,
        patience=args.patience, max_len=args.max_len,
        sgd_epochs_per_chunk=args.sgd_epochs_per_chunk,
        sgd_max_features=args.sgd_max_features,
        calibrate=args.calibrate, save_per_example=args.save_per_example,
        n_bins=args.n_bins, latency_examples=args.latency_examples,
        latency_warmup=args.latency_warmup, models=models, run_id=run_id,
        command=command,
    )

    raw = pd.DataFrame(raw_rows)
    metrics = pd.DataFrame(model_metric_rows)

    agg_dir = out_root / "aggregated"
    agg_dir.mkdir(parents=True, exist_ok=True)
    summary_path = agg_dir / f"{run_id}_summary.csv"
    if not raw.empty:
        summary = aggregate_raw(raw, summary_path)
    else:
        summary = pd.DataFrame()
        summary.to_csv(summary_path, index=False)

    metrics_summary_path = agg_dir / f"{run_id}_model_metrics_summary.csv"
    if not metrics.empty:
        aggregate_model_metrics(metrics, metrics_summary_path)

    matrix_overall = write_run_matrix(raw, models, seeds, args.num_chunks, agg_dir)
    # Prefix matrix files with run id as well.
    for name in ("run_matrix.csv", "run_matrix_summary.csv", "run_matrix_overall.json"):
        src = agg_dir / name
        if src.exists():
            shutil.copyfile(src, agg_dir / f"{run_id}_{name}")

    fig_dir = out_root / "figures" / run_id
    from plot_results import plot_all
    fig_manifest = plot_all(run_dir, fig_dir)
    figures = [fig_dir / name for name in fig_manifest.get("figures", {})]

    lock_path = out_root / "locks" / f"{run_id}.json"
    agg_files = {
        "summary": str(summary_path),
        "model_metrics_summary": str(metrics_summary_path),
        "run_matrix": str(agg_dir / f"{run_id}_run_matrix.csv"),
        "run_matrix_summary": str(agg_dir / f"{run_id}_run_matrix_summary.csv"),
        "run_matrix_overall": str(agg_dir / f"{run_id}_run_matrix_overall.json"),
        "figure_manifest": str(fig_dir / "figure_manifest.json"),
        "lock": str(lock_path),
    }
    report_path = _write_report(run_dir, manifest, summary, matrix_overall,
                                fig_dir, figures, agg_files, lock_path, command)

    files = [p for p in run_dir.iterdir() if p.is_file()]
    files += [summary_path, metrics_summary_path]
    files += [agg_dir / f"{run_id}_{n}" for n in
              ("run_matrix.csv", "run_matrix_summary.csv", "run_matrix_overall.json")]
    files += figures
    files += [fig_dir / "figure_manifest.json"]
    lock = lock_outputs(run_dir, [p for p in files if p.exists()], lock_path,
                        extra={"run_id": run_id, "command": command,
                               "status": matrix_overall.get("status"),
                               "dataset_sha256": integrity.get("actual_sha256"),
                               "git_head": manifest.get("source", {}).get("git_head")})
    (out_root / "locks" / f"{run_id}.locked").write_text(
        f"locked {run_id}\n{utc_now()}\n", encoding="utf-8")

    print("\n=== Run matrix ===")
    print(json.dumps(matrix_overall, indent=2))
    print("\n=== Final-step accuracy (mean +/- std) ===")
    if not summary.empty:
        final_step = int(summary["chunk_step"].max())
        cols = [c for c in ["model", "eval_chunk", "accuracy_mean", "accuracy_std",
                            "accuracy_ci95_low", "accuracy_ci95_high"]
                if c in summary.columns]
        print(summary[summary["chunk_step"] == final_step][cols].round(4).to_string(index=False))
    print(f"\nRun dir: {run_dir}")
    print(f"Summary: {summary_path}")
    print(f"Figures: {fig_dir}")
    print(f"Report: {report_path}")
    print(f"Lock: {lock_path}")
    print(f"Completed: {matrix_overall.get('completed_cells')}/{matrix_overall.get('expected_cells')} "
          f"({matrix_overall.get('status')})")
    return 0 if matrix_overall.get("status") == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

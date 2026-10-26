"""CSV-only figures for the liquid streaming study.

Every figure in this module is produced from files already saved by a run:
  raw_results.csv
  per_example_predictions.csv
  model_metrics.csv
  learning_curves.csv

No model is trained, no dataset is loaded, and no metric is recomputed from
predictions except reliability bins and an ECE cross-check from the saved
per-example probabilities.

Usage:
    python src/plot_results.py --run-dir outputs/runs/<run_id> --out outputs/figures
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODEL_ORDER = ["cfc", "cfc_ablation_pure", "cfc_ablation_no_gate",
               "lstm", "gru", "tfidf_sgd"]
MODEL_LABELS = {
    "cfc": "CfC",
    "cfc_ablation_pure": "CfC (pure mode)",
    "cfc_ablation_no_gate": "CfC (no-gate mode)",
    "lstm": "LSTM",
    "gru": "GRU",
    "tfidf_sgd": "TF-IDF+SGD",
}
COLORS = {
    "cfc": "#1f77b4",
    "cfc_ablation_pure": "#17becf",
    "cfc_ablation_no_gate": "#9467bd",
    "lstm": "#ff7f0e",
    "gru": "#2ca02c",
    "tfidf_sgd": "#d62728",
}


def _present(df: pd.DataFrame) -> List[str]:
    return [m for m in MODEL_ORDER if m in set(df["model"].unique())]


def _mean_std(df: pd.DataFrame, group: List[str], value: str):
    return (df.groupby(group)[value]
              .agg(["mean", "std", "count"]).reset_index())


def _save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def plot_adaptation(raw: pd.DataFrame, fig_dir: Path) -> List[Path]:
    paths: List[Path] = []
    models = _present(raw)

    current = raw[raw["eval_chunk"] == raw["chunk_step"]].copy()
    if not current.empty:
        agg = _mean_std(current, ["model", "chunk_step"], "accuracy")
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        for model in models:
            g = agg[agg["model"] == model].sort_values("chunk_step")
            if g.empty:
                continue
            ax.errorbar(g["chunk_step"], g["mean"],
                        yerr=g["std"].fillna(0), marker="o", capsize=3,
                        label=MODEL_LABELS.get(model, model),
                        color=COLORS.get(model))
        ax.set_xlabel("Chunk step (new intents arrive)")
        ax.set_ylabel("Accuracy on current/new chunk")
        ax.set_ylim(0, 1)
        ax.set_xticks(sorted(current["chunk_step"].unique()))
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        ax.set_title("Current-chunk adaptation (mean +/- seed std)")
        paths.append(_save(fig, fig_dir / "adaptation_current_chunk.png"))

    overall = (raw.groupby(["seed", "model", "chunk_step"])["accuracy"]
                  .mean().reset_index().rename(columns={"accuracy": "accuracy_over_seen"}))
    if not overall.empty:
        agg = _mean_std(overall, ["model", "chunk_step"], "accuracy_over_seen")
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        for model in models:
            g = agg[agg["model"] == model].sort_values("chunk_step")
            if g.empty:
                continue
            ax.errorbar(g["chunk_step"], g["mean"],
                        yerr=g["std"].fillna(0), marker="o", capsize=3,
                        label=MODEL_LABELS.get(model, model),
                        color=COLORS.get(model))
        ax.set_xlabel("Chunk step")
        ax.set_ylabel("Mean accuracy over all seen chunks")
        ax.set_ylim(0, 1)
        ax.set_xticks(sorted(overall["chunk_step"].unique()))
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
        ax.set_title("Overall seen-chunk accuracy (mean +/- seed std)")
        paths.append(_save(fig, fig_dir / "adaptation_mean_seen_chunks.png"))
    return paths


def plot_retention_forgetting(raw: pd.DataFrame, fig_dir: Path) -> List[Path]:
    paths: List[Path] = []
    models = _present(raw)
    ncols = 3
    nrows = int(np.ceil(len(models) / ncols)) if models else 0
    if not models:
        return paths

    mean_acc = (raw.groupby(["model", "chunk_step", "eval_chunk"])["accuracy"]
                   .mean().reset_index())
    vmax = 1.0
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.5 * nrows),
                             squeeze=False)
    for ax in axes.ravel():
        ax.axis("off")
    for ax, model in zip(axes.ravel(), models):
        g = mean_acc[mean_acc["model"] == model]
        steps = sorted(g["chunk_step"].unique())
        evals = sorted(g["eval_chunk"].unique())
        mat = np.full((len(evals), len(steps)), np.nan)
        for _, row in g.iterrows():
            mat[evals.index(row["eval_chunk"]), steps.index(row["chunk_step"])] = row["accuracy"]
        ax.axis("on")
        im = ax.imshow(mat, vmin=0, vmax=vmax, cmap="viridis", aspect="auto")
        ax.set_xticks(range(len(steps)))
        ax.set_xticklabels([f"t={s}" for s in steps])
        ax.set_yticks(range(len(evals)))
        ax.set_yticklabels([f"task {e}" for e in evals])
        ax.set_xlabel("After training on chunk")
        ax.set_ylabel("Evaluated old task")
        ax.set_title(MODEL_LABELS.get(model, model), fontsize=9)
        for i in range(len(evals)):
            for j in range(len(steps)):
                if np.isfinite(mat[i, j]):
                    ax.text(j, i, f"{mat[i, j]:.2f}", ha="center", va="center",
                            fontsize=7, color="white" if mat[i, j] < 0.55 else "black")
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.7, label="Mean accuracy")
    fig.suptitle("Old-task retention after each chunk (mean over seeds)")
    paths.append(_save(fig, fig_dir / "retention_by_model.png"))

    # Retention / forgetting of previously seen tasks after each new chunk.
    per_seed = (raw.groupby(["seed", "model", "chunk_step", "eval_chunk"])["accuracy"]
                   .mean().reset_index())
    rows = []
    for (seed, model), g in per_seed.groupby(["seed", "model"]):
        pivot = g.pivot(index="eval_chunk", columns="chunk_step", values="accuracy")
        steps = sorted(pivot.columns)
        for t in steps:
            old = [e for e in pivot.index if e < t and np.isfinite(pivot.loc[e, t])]
            if not old:
                continue
            retention = float(np.mean([pivot.loc[e, t] for e in old]))
            forgetting = []
            for e in old:
                seen = [pivot.loc[e, s] for s in steps if s <= t and np.isfinite(pivot.loc[e, s])]
                if seen:
                    forgetting.append(max(seen) - pivot.loc[e, t])
            rows.append({"seed": seed, "model": model, "chunk_step": t,
                         "old_task_retention": retention,
                         "forgetting": float(np.mean(forgetting)) if forgetting else np.nan})
    if rows:
        df = pd.DataFrame(rows)
        agg_ret = _mean_std(df, ["model", "chunk_step"], "old_task_retention")
        agg_for = _mean_std(df, ["model", "chunk_step"], "forgetting")
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), sharex=True)
        for model in models:
            g = agg_ret[agg_ret["model"] == model].sort_values("chunk_step")
            if not g.empty:
                axes[0].errorbar(g["chunk_step"], g["mean"], yerr=g["std"].fillna(0),
                                 marker="o", capsize=3, label=MODEL_LABELS.get(model, model),
                                 color=COLORS.get(model))
            g = agg_for[agg_for["model"] == model].sort_values("chunk_step")
            if not g.empty:
                axes[1].errorbar(g["chunk_step"], g["mean"], yerr=g["std"].fillna(0),
                                 marker="o", capsize=3, label=MODEL_LABELS.get(model, model),
                                 color=COLORS.get(model))
        axes[0].set_title("Mean accuracy on previously seen tasks")
        axes[0].set_ylabel("Old-task retention")
        axes[1].set_title("Forgetting of previously seen tasks")
        axes[1].set_ylabel("max prior accuracy - current accuracy")
        for ax in axes:
            ax.set_xlabel("After training on chunk step")
            ax.set_xticks(sorted(df["chunk_step"].unique()))
            ax.grid(alpha=0.3)
        axes[0].set_ylim(0, 1)
        axes[0].legend(fontsize=7)
        fig.suptitle("Retention and forgetting after each chunk (mean +/- seed std)")
        paths.append(_save(fig, fig_dir / "forgetting_after_each_chunk.png"))
    return paths


def plot_model_size_latency(metrics: pd.DataFrame, fig_dir: Path) -> List[Path]:
    if metrics is None or metrics.empty:
        return []
    models = [m for m in MODEL_ORDER if m in set(metrics["model"].unique())]
    agg = _mean_std(metrics, ["model"], "serialized_size_mb")
    lat = _mean_std(metrics, ["model"], "latency_p50_ms")
    lat95 = _mean_std(metrics, ["model"], "latency_p95_ms")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    x = np.arange(len(models))
    size_map = {r["model"]: r for _, r in agg.iterrows()}
    lat_map = {r["model"]: r for _, r in lat.iterrows()}
    lat95_map = {r["model"]: r for _, r in lat95.iterrows()}
    axes[0].bar(x, [size_map[m]["mean"] for m in models],
                yerr=[size_map[m]["std"] for m in models], capsize=4,
                color=[COLORS.get(m) for m in models], alpha=0.85)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("Serialized size (MB, log scale)")
    axes[0].set_title("Model size")
    axes[1].bar(x, [lat_map[m]["mean"] for m in models],
                yerr=[lat_map[m]["std"] for m in models], capsize=4,
                color=[COLORS.get(m) for m in models], alpha=0.85)
    axes[1].errorbar(x, [lat95_map[m]["mean"] for m in models],
                     yerr=[lat95_map[m]["std"] for m in models],
                     fmt="none", ecolor="black", capsize=3, label="p95")
    axes[1].set_ylabel("Single-example latency (ms)")
    axes[1].set_title("Inference latency (p50 bars, p95 whiskers)")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels([MODEL_LABELS.get(m, m) for m in models], rotation=20,
                           ha="right", fontsize=8)
        ax.grid(alpha=0.3, axis="y")
    fig.suptitle("Model size and CPU inference latency (mean +/- seed std)")
    return [_save(fig, fig_dir / "model_size_latency.png")]


def _reliability(conf: np.ndarray, correct: np.ndarray, n_bins: int):
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    xs, ys, counts = [], [], []
    ece = 0.0
    n = len(conf)
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (conf > lo) & (conf <= hi)
        c = int(mask.sum())
        if c == 0:
            continue
        avg_conf = float(conf[mask].mean())
        acc = float(correct[mask].mean())
        xs.append(avg_conf)
        ys.append(acc)
        counts.append(c)
        ece += (c / max(1, n)) * abs(acc - avg_conf)
    return xs, ys, counts, ece


def plot_calibration(per_example: Optional[pd.DataFrame], raw: pd.DataFrame,
                     fig_dir: Path) -> List[Path]:
    paths: List[Path] = []
    if per_example is not None and not per_example.empty:
        models = [m for m in MODEL_ORDER if m in set(per_example["model"].unique())]
        final_step = int(raw["chunk_step"].max()) if not raw.empty else int(per_example["chunk_step"].max())
        sub = per_example[per_example["chunk_step"] == final_step]
        n_bins = int(raw["n_calibration_bins"].iloc[0]) if "n_calibration_bins" in raw else 15
        ncols = 3
        nrows = int(np.ceil(len(models) / ncols)) if models else 0
        if models:
            fig, axes = plt.subplots(nrows, ncols, figsize=(4.0 * ncols, 3.6 * nrows),
                                     squeeze=False)
            for ax in axes.ravel():
                ax.axis("off")
            for ax, model in zip(axes.ravel(), models):
                g = sub[sub["model"] == model]
                if g.empty:
                    continue
                ax.axis("on")
                conf = pd.to_numeric(g["confidence_calibrated"], errors="coerce").to_numpy(dtype=float)
                correct = pd.to_numeric(g["correct"], errors="coerce").to_numpy(dtype=float)
                mask = np.isfinite(conf) & np.isfinite(correct)
                conf, correct = conf[mask], correct[mask]
                xs, ys, counts, ece = _reliability(conf, correct, n_bins)
                ax.plot([0, 1], [0, 1], "--", color="grey", label="ideal")
                ax.bar(xs, ys, width=1.0 / n_bins, alpha=0.55,
                       color=COLORS.get(model), edgecolor="black", linewidth=0.4,
                       label="calibrated")
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_xlabel("Mean confidence")
                ax.set_ylabel("Empirical accuracy")
                ax.set_title(f"{MODEL_LABELS.get(model, model)}\nECE={ece:.3f}, n={len(conf)}",
                             fontsize=9)
                ax.grid(alpha=0.25)
            fig.suptitle(f"Calibration reliability at final chunk step {final_step} (calibrated probabilities, all seeds)")
            paths.append(_save(fig, fig_dir / "calibration_reliability.png"))

    if not raw.empty:
        final_step = int(raw["chunk_step"].max())
        sub = raw[raw["chunk_step"] == final_step]
        if not sub.empty:
            models = [m for m in MODEL_ORDER if m in set(sub["model"].unique())]
            metrics = ["ece_calibrated", "ece_uncalibrated", "brier_calibrated",
                       "brier_uncalibrated"]
            fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
            x = np.arange(len(models))
            width = 0.18
            for i, m in enumerate(metrics):
                agg = _mean_std(sub, ["model"], m)
                amap = {r["model"]: r for _, r in agg.iterrows()}
                vals = [amap[model]["mean"] if model in amap else np.nan for model in models]
                errs = [amap[model]["std"] if model in amap else np.nan for model in models]
                axes[0 if "ece" in m else 1].bar(
                    x + (i % 2 - 0.5) * width, vals, width=width,
                    yerr=errs, capsize=3, label=m.replace("_", " "))
            axes[0].set_ylabel("ECE (lower is better)")
            axes[0].set_title("Expected calibration error")
            axes[1].set_ylabel("Brier score (lower is better)")
            axes[1].set_title("Brier score")
            for ax in axes:
                ax.set_xticks(x)
                ax.set_xticklabels([MODEL_LABELS.get(m, m) for m in models],
                                   rotation=20, ha="right", fontsize=8)
                ax.grid(alpha=0.3, axis="y")
                ax.legend(fontsize=7)
            fig.suptitle(f"Calibration and Brier at final chunk step {final_step} (mean +/- seed std)")
            paths.append(_save(fig, fig_dir / "calibration_ece_brier.png"))
    return paths


def plot_learning_curves(learning: Optional[pd.DataFrame], fig_dir: Path) -> List[Path]:
    if learning is None or learning.empty or "val_accuracy" not in learning:
        return []
    models = [m for m in MODEL_ORDER if m in set(learning["model"].unique())]
    ncols = 3
    nrows = int(np.ceil(len(models) / ncols)) if models else 0
    if not models:
        return []
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.4 * nrows),
                             squeeze=False)
    for ax in axes.ravel():
        ax.axis("off")
    for ax, model in zip(axes.ravel(), models):
        g = learning[learning["model"] == model]
        if g.empty:
            continue
        ax.axis("on")
        agg = _mean_std(g, ["chunk_step", "epoch"], "val_accuracy")
        for step, sg in agg.groupby("chunk_step"):
            sg = sg.sort_values("epoch")
            ax.plot(sg["epoch"], sg["mean"], marker=".", label=f"chunk {int(step)}")
        ax.set_ylim(0, 1)
        ax.set_xlabel("Epoch within chunk")
        ax.set_ylabel("Validation accuracy")
        ax.set_title(MODEL_LABELS.get(model, model), fontsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=6)
    fig.suptitle("Within-chunk validation learning curves (mean over seeds)")
    fig.tight_layout()
    path = fig_dir / "within_chunk_learning_curves.png"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return [path]


def plot_all(run_dir: Path, out_dir: Path) -> Dict:
    run_dir = Path(run_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(run_dir / "raw_results.csv")
    per_example_path = run_dir / "per_example_predictions.csv"
    metrics_path = run_dir / "model_metrics.csv"
    learning_path = run_dir / "learning_curves.csv"
    per_example = pd.read_csv(per_example_path) if per_example_path.exists() else None
    metrics = pd.read_csv(metrics_path) if metrics_path.exists() else None
    learning = pd.read_csv(learning_path) if learning_path.exists() else None

    figures: List[Path] = []
    figures += plot_adaptation(raw, out_dir)
    figures += plot_retention_forgetting(raw, out_dir)
    figures += plot_model_size_latency(metrics, out_dir)
    figures += plot_calibration(per_example, raw, out_dir)
    figures += plot_learning_curves(learning, out_dir)

    from study_utils import sha256_file, utc_now
    manifest = {
        "generated_at_utc": utc_now(),
        "run_dir": str(run_dir.resolve()),
        "out_dir": str(out_dir.resolve()),
        "inputs": {
            p.name: {"sha256": sha256_file(p), "byte_size": p.stat().st_size}
            for p in [run_dir / "raw_results.csv", per_example_path,
                      metrics_path, learning_path] if p.exists()
        },
        "figures": {
            p.name: {"sha256": sha256_file(p), "byte_size": p.stat().st_size}
            for p in figures if p.exists()
        },
        "note": "All figures were generated from saved CSVs only; no training was performed.",
    }
    (out_dir / "figure_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"figures written: {len(figures)} -> {out_dir}")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description="Regenerate all study figures from saved CSVs")
    ap.add_argument("--run-dir", required=True,
                    help="Directory containing raw_results.csv etc.")
    ap.add_argument("--out", default=None, help="Figure output directory")
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    out_dir = Path(args.out) if args.out else run_dir.parent.parent / "figures"
    plot_all(run_dir, out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Figures for the liquid streaming study, plotted from saved CSVs (never recomputed)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MODEL_NAMES = {"cfc": "CfC (liquid)", "lstm": "LSTM", "gru": "GRU", "tfidf_sgd": "TF-IDF+SGD"}
MODEL_ORDER = ["cfc", "lstm", "gru", "tfidf_sgd"]


def _overall_seen(df: pd.DataFrame) -> pd.DataFrame:
    """Mean accuracy across all seen chunks per (seed, model, chunk_step)."""
    g = df.groupby(["seed", "model", "chunk_step"])["accuracy"].mean().reset_index()
    g = g.rename(columns={"accuracy": "accuracy_over_seen"})
    return g


def _latest_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """Accuracy on the newest (current) chunk only: eval_chunk == chunk_step."""
    sub = df[df["eval_chunk"] == df["chunk_step"]].copy()
    return sub


def _agg(sub: pd.DataFrame, value_col: str):
    return (sub.groupby("model")[value_col]
              .agg(["mean", "std"])
              .reindex(MODEL_ORDER))


def plot_accuracy_vs_chunk(raw_df: pd.DataFrame, fig_dir: Path):
    fig_dir = Path(fig_dir)
    fig_dir.mkdir(parents=True, exist_ok=True)

    overall = _overall_seen(raw_df)
    latest = _latest_chunk(raw_df)

    x = np.array(sorted(overall["chunk_step"].unique()))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, sub, title, ycol in (
        (axes[0], overall, "Mean accuracy over ALL seen chunks", "accuracy_over_seen"),
        (axes[1], latest, "Adaptation: accuracy on the NEWEST chunk only", "accuracy"),
    ):
        for name in MODEL_ORDER:
            m = sub[sub["model"] == name].sort_values("chunk_step")
            if m.empty:
                continue
            ax.plot(m["chunk_step"], m[ycol], marker="o", label=MODEL_NAMES[name])
        ax.set_xlabel("Chunk step (arriving intent block)")
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.3)
        ax.legend()
    axes[0].set_ylabel("Accuracy")
    fig.suptitle("Class-incremental intent stream (CLINC150, 5 chunks x 30 intents)")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(fig_dir / "accuracy_vs_chunk.png", dpi=150)
    plt.close(fig)

    # per-model variability at the final step (bar chart with seed std)
    final_overall = overall[overall["chunk_step"] == overall["chunk_step"].max()]
    means = final_overall.groupby("model")["accuracy_over_seen"].mean().reindex(MODEL_ORDER)
    stds = final_overall.groupby("model")["accuracy_over_seen"].std().reindex(MODEL_ORDER).fillna(0)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([MODEL_NAMES[m] for m in MODEL_ORDER], means.values,
           yerr=stds.values, capsize=5, alpha=0.8)
    ax.set_ylabel("Final mean accuracy over all seen chunks")
    ax.set_ylim(0, 1)
    ax.set_title("Final-step accuracy by model (mean +/- std across seeds)")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(fig_dir / "final_step_accuracy.png", dpi=150)
    plt.close(fig)
    print(f"figures written to {fig_dir}")

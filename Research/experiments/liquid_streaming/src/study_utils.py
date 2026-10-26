"""Shared reproducibility, aggregation, run-matrix and locking utilities.

This module intentionally has no training imports.  It can be used by the
preflight check, the study runner and the CSV-only plotting script.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _pkg_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def environment_info(root: Optional[Path] = None) -> Dict:
    """Record the interpreter, packages, hardware, disk and OS details."""
    free_gb = None
    total_gb = None
    try:
        usage = shutil.disk_usage(str(root) if root else os.getcwd())
        free_gb = round(usage.free / (1024 ** 3), 3)
        total_gb = round(usage.total / (1024 ** 3), 3)
    except Exception:
        pass
    info = {
        "timestamp_utc": utc_now(),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version,
        "python_executable": sys.executable,
        "cpu_count": os.cpu_count(),
        "disk": {"free_gb": free_gb, "total_gb": total_gb},
        "packages": {
            "numpy": _pkg_version("numpy"),
            "pandas": _pkg_version("pandas"),
            "scipy": _pkg_version("scipy"),
            "scikit-learn": _pkg_version("scikit-learn"),
            "torch": _pkg_version("torch"),
            "ncps": _pkg_version("ncps"),
            "matplotlib": _pkg_version("matplotlib"),
        },
    }
    try:
        import torch
        info["cuda_available"] = bool(torch.cuda.is_available())
        info["torch_threads"] = int(torch.get_num_threads())
        info["torch_deterministic_algorithms"] = bool(torch.are_deterministic_algorithms_enabled())
    except Exception as e:  # pragma: no cover - reporting only
        info["torch_error"] = str(e)
    return info


def _run_git(args: Sequence[str], root: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", *args], cwd=str(root), stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except Exception:
        return ""


def source_revision(root: Path) -> Dict:
    """Git revision + hashes of the study's source files."""
    root = Path(root)
    src_dir = root / "src"
    files = sorted([p for p in src_dir.glob("*.py")] +
                   [p for p in root.glob("*.py")])
    file_hashes = {str(p.relative_to(root)): sha256_file(p) for p in files}
    return {
        "git_head": _run_git(["rev-parse", "HEAD"], root),
        "git_head_short": _run_git(["rev-parse", "--short", "HEAD"], root),
        "git_branch": _run_git(["rev-parse", "--abbrev-ref", "HEAD"], root),
        "git_status_porcelain": _run_git(["status", "--porcelain"], root),
        "source_file_sha256": file_hashes,
    }


def dataset_integrity(data_dir: Path) -> Dict:
    """Verify the dataset against data/dataset_manifest.json."""
    data_dir = Path(data_dir)
    manifest_path = data_dir / "dataset_manifest.json"
    out: Dict = {
        "data_dir": str(data_dir.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "manifest_present": manifest_path.exists(),
        "ok": False,
    }
    if not manifest_path.exists():
        out["error"] = "dataset_manifest.json is missing"
        return out
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    out["manifest"] = manifest
    file_name = manifest.get("file")
    if not file_name:
        out["error"] = "manifest has no 'file' entry"
        return out
    data_path = data_dir / file_name
    out["file"] = str(data_path.resolve())
    if not data_path.exists():
        out["error"] = f"dataset file not found: {data_path}"
        return out
    actual_sha = sha256_file(data_path)
    actual_size = data_path.stat().st_size
    expected_sha = manifest.get("sha256")
    expected_size = manifest.get("byte_size")
    out.update({
        "actual_sha256": actual_sha,
        "actual_byte_size": actual_size,
        "expected_sha256": expected_sha,
        "expected_byte_size": expected_size,
        "sha256_match": actual_sha == expected_sha,
        "size_match": expected_size is None or actual_size == expected_size,
    })
    out["ok"] = bool(out["sha256_match"] and out["size_match"])
    return out


def _ci95(values: pd.Series) -> tuple:
    """Two-sided 95% CI from a t distribution over independent seed values."""
    vals = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    n = len(vals)
    if n < 2:
        return (float("nan"), float("nan"), float("nan"), n)
    mean = float(vals.mean())
    std = float(vals.std(ddof=1))
    se = std / np.sqrt(n)
    try:
        from scipy.stats import t
        crit = float(t.ppf(0.975, df=n - 1))
    except Exception:
        crit = float("nan")
    half = crit * se if np.isfinite(crit) else float("nan")
    return (mean, std, half, n)


def aggregate_raw(raw: pd.DataFrame, out_path: Path,
                  metrics: Sequence[str] = ("accuracy", "ece_calibrated",
                                            "brier_calibrated",
                                            "ece_uncalibrated",
                                            "brier_uncalibrated")) -> pd.DataFrame:
    """Aggregate per-seed rows to mean/std/95%-t-CI per model/chunk cell."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    metrics = [m for m in metrics if m in raw.columns]
    rows: List[Dict] = []
    group_cols = ["model", "chunk_step", "eval_chunk"]
    for keys, g in raw.groupby(group_cols, dropna=False):
        key = dict(zip(group_cols, keys if isinstance(keys, tuple) else (keys,)))
        row: Dict = dict(key)
        row["n_seeds"] = int(g["seed"].nunique())
        row["seeds"] = ";".join(str(s) for s in sorted(g["seed"].unique()))
        for m in metrics:
            mean, std, half, n = _ci95(g[m])
            row[f"{m}_mean"] = mean
            row[f"{m}_std"] = std
            row[f"{m}_ci95_low"] = mean - half if np.isfinite(half) else float("nan")
            row[f"{m}_ci95_high"] = mean + half if np.isfinite(half) else float("nan")
            row[f"{m}_n"] = n
        rows.append(row)
    summary = pd.DataFrame(rows).sort_values(group_cols).reset_index(drop=True)
    summary.to_csv(out_path, index=False)
    meta = {
        "generated_at_utc": utc_now(),
        "source": "per-seed raw_results.csv",
        "grouping": group_cols,
        "metrics": list(metrics),
        "mean": "arithmetic mean over seeds",
        "std": "sample standard deviation over seeds (pandas ddof=1)",
        "ci95": "two-sided t-distribution CI: mean +/- t(0.975, df=n-1) * std/sqrt(n)",
        "ci_requires": "at least 2 independent seeds; otherwise CI fields are NaN",
        "n_seeds": "number of distinct seeds contributing to the cell",
    }
    out_path.with_name(out_path.stem + "_metadata.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    return summary


def aggregate_model_metrics(metrics: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    numeric = ["n_params", "serialized_size_mb", "latency_p50_ms",
               "latency_p95_ms", "latency_mean_ms",
               "throughput_examples_per_sec"]
    rows: List[Dict] = []
    for model, g in metrics.groupby("model"):
        row = {"model": model, "n_seeds": int(g["seed"].nunique())}
        for m in numeric:
            if m not in g.columns:
                continue
            mean, std, half, n = _ci95(g[m])
            row[f"{m}_mean"] = mean
            row[f"{m}_std"] = std
            row[f"{m}_ci95_low"] = mean - half if np.isfinite(half) else float("nan")
            row[f"{m}_ci95_high"] = mean + half if np.isfinite(half) else float("nan")
        rows.append(row)
    summary = pd.DataFrame(rows).sort_values("model").reset_index(drop=True)
    summary.to_csv(out_path, index=False)
    return summary


def write_run_matrix(raw: pd.DataFrame, models: Sequence[str], seeds: Sequence[int],
                     num_chunks: int, out_dir: Path) -> Dict:
    """Write the planned-vs-completed cell matrix and a compact summary."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    expected: List[Dict] = []
    for model in models:
        for seed in seeds:
            for chunk_step in range(num_chunks):
                for eval_chunk in range(chunk_step + 1):
                    expected.append({
                        "model": model, "seed": int(seed),
                        "chunk_step": chunk_step, "eval_chunk": eval_chunk,
                    })
    expected_df = pd.DataFrame(expected)
    actual_cols = ["model", "seed", "chunk_step", "eval_chunk", "accuracy",
                   "temperature", "ece_calibrated", "brier_calibrated"]
    actual_cols = [c for c in actual_cols if c in raw.columns]
    actual = raw[actual_cols].copy()
    matrix = expected_df.merge(actual, on=["model", "seed", "chunk_step", "eval_chunk"],
                               how="left")
    matrix["completed"] = matrix["accuracy"].notna()
    matrix["status"] = np.where(matrix["completed"], "completed", "missing")
    matrix.to_csv(out_dir / "run_matrix.csv", index=False)

    summaries: List[Dict] = []
    for (model, seed), g in matrix.groupby(["model", "seed"]):
        per_step = []
        for step, sg in g.groupby("chunk_step"):
            per_step.append({
                "chunk_step": int(step),
                "expected": int(len(sg)),
                "completed": int(sg["completed"].sum()),
                "missing": int((~sg["completed"]).sum()),
                "status": "completed" if bool(sg["completed"].all()) else "partial",
            })
        summaries.append({
            "model": model, "seed": int(seed),
            "expected_cells": int(len(g)),
            "completed_cells": int(g["completed"].sum()),
            "missing_cells": int((~g["completed"]).sum()),
            "status": "completed" if bool(g["completed"].all()) else "partial",
            "per_chunk_step": json.dumps(per_step),
        })
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(out_dir / "run_matrix_summary.csv", index=False)

    overall = {
        "generated_at_utc": utc_now(),
        "models": list(models),
        "seeds": [int(s) for s in seeds],
        "num_chunks": int(num_chunks),
        "expected_cells": int(len(matrix)),
        "completed_cells": int(matrix["completed"].sum()),
        "missing_cells": int((~matrix["completed"]).sum()),
        "status": "completed" if bool(matrix["completed"].all()) else "partial",
        "definition": "one cell = model x seed x chunk_step x eval_chunk (eval_chunk <= chunk_step)",
    }
    (out_dir / "run_matrix_overall.json").write_text(
        json.dumps(overall, indent=2), encoding="utf-8")
    return overall


def lock_outputs(run_dir: Path, files: Iterable[Path], lock_path: Path,
                 extra: Optional[Dict] = None) -> Dict:
    run_dir = Path(run_dir)
    lock_path = Path(lock_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    entries = {}
    for f in files:
        f = Path(f)
        if f.exists() and f.is_file():
            entries[str(f.relative_to(run_dir)) if f.is_relative_to(run_dir) else str(f)] = {
                "sha256": sha256_file(f),
                "byte_size": f.stat().st_size,
            }
    payload = {
        "locked": True,
        "locked_at_utc": utc_now(),
        "run_dir": str(run_dir.resolve()),
        "files": entries,
        "note": "Hashes pin the exact CSV/JSON/PNG files produced by this run.",
    }
    if extra:
        payload.update(extra)
    lock_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

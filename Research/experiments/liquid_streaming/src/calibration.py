"""Calibration utilities: temperature scaling (fit on val), ECE, Brier score.

Temperature scaling is applied *after* training using logits from the
validation split only.  Test predictions are never used to fit the
temperature.  The fitted temperature is then applied to test logits to
produce calibrated probabilities for ECE / Brier computation.

Reference: Guo et al., "On Calibration of Modern Neural Networks" (ICML 2017).
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Numerically stable softmax."""
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)


def fit_temperature(logits: np.ndarray, labels: np.ndarray) -> float:
    """Fit a single temperature T > 0 on val logits/labels by minimizing NLL.

    Parameters
    ----------
    logits : (N, C) raw model logits on the validation split.
    labels : (N,) integer true class indices.

    Returns
    -------
    float : optimal temperature T.
    """
    from scipy.optimize import minimize_scalar

    def nll(T: float) -> float:
        probs = softmax(logits / T, axis=1)
        probs = np.clip(probs, 1e-12, 1.0)
        return float(-np.mean(np.log(probs[np.arange(len(labels)), labels])))

    res = minimize_scalar(nll, bounds=(1e-3, 200.0), method="bounded")
    if not res.success:
        # fall back to T=1.0 (no calibration) if optimisation fails
        return 1.0
    return float(res.x)


def apply_temperature(logits: np.ndarray, temperature: float) -> np.ndarray:
    """Apply temperature scaling to logits and return calibrated probabilities."""
    return softmax(logits / temperature, axis=1)


def compute_ece(
    probs: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 15,
) -> Dict:
    """Expected Calibration Error with per-bin reliability statistics.

    Parameters
    ----------
    probs : (N, C) calibrated or uncalibrated class probabilities.
    labels : (N,) integer true class indices.
    n_bins : number of equal-width confidence bins.

    Returns
    -------
    dict with keys:
        ece            : expected calibration error (float)
        brier          : multi-class Brier score (float)
        n_bins         : int
        bins           : list of per-bin dicts
                         {bin_lower, bin_upper, count, accuracy, avg_confidence, gap}
    """
    confidences = probs.max(axis=1)
    predictions = probs.argmax(axis=1)
    accuracies = (predictions == labels).astype(float)

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]

    ece = 0.0
    bins: List[Dict] = []
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = float(in_bin.mean())
        if prop_in_bin > 0.0:
            accuracy_in_bin = float(accuracies[in_bin].mean())
            avg_confidence_in_bin = float(confidences[in_bin].mean())
            gap = abs(avg_confidence_in_bin - accuracy_in_bin)
            ece += gap * prop_in_bin
            bins.append({
                "bin_lower": float(bin_lower),
                "bin_upper": float(bin_upper),
                "count": int(in_bin.sum()),
                "accuracy": accuracy_in_bin,
                "avg_confidence": avg_confidence_in_bin,
                "gap": gap,
            })
        else:
            bins.append({
                "bin_lower": float(bin_lower),
                "bin_upper": float(bin_upper),
                "count": 0,
                "accuracy": 0.0,
                "avg_confidence": 0.0,
                "gap": 0.0,
            })

    # Multi-class Brier score: mean over examples of sum over classes (p - y)^2
    one_hot = np.eye(probs.shape[1])[labels]
    brier = float(((probs - one_hot) ** 2).sum(axis=1).mean())

    return {
        "ece": float(ece),
        "brier": brier,
        "n_bins": n_bins,
        "bins": bins,
    }
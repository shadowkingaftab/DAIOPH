"""Classification metrics: accuracy, precision, recall, F1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

__all__ = ["Evaluator", "Metrics"]


@dataclass(frozen=True)
class Metrics:
    """Evaluation metrics for one label or the macro average."""

    accuracy: float
    precision: float
    recall: float
    f1: float
    support: int


class Evaluator:
    """Computes deterministic classification metrics."""

    @staticmethod
    def accuracy(truth: Sequence[str], pred: Sequence[str]) -> float:
        """Fraction of matching labels (0.0 for empty input)."""
        if len(truth) != len(pred):
            raise ValueError("truth and pred must have equal length")
        if not truth:
            return 0.0
        return sum(t == p for t, p in zip(truth, pred)) / len(truth)

    @staticmethod
    def per_label(truth: Sequence[str], pred: Sequence[str]) -> Dict[str, Metrics]:
        """Precision/recall/F1 per distinct label plus overall accuracy."""
        if len(truth) != len(pred):
            raise ValueError("truth and pred must have equal length")
        labels: List[str] = []
        for label in list(truth) + list(pred):
            if label not in labels:
                labels.append(label)
        overall_acc = Evaluator.accuracy(truth, pred)
        result: Dict[str, Metrics] = {}
        for label in labels:
            tp = sum(
                1 for t, p in zip(truth, pred) if t == label and p == label
            )
            fp = sum(
                1 for t, p in zip(truth, pred) if t != label and p == label
            )
            fn = sum(
                1 for t, p in zip(truth, pred) if t == label and p != label
            )
            support = sum(1 for t in truth if t == label)
            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = (
                2 * precision * recall / (precision + recall)
                if (precision + recall)
                else 0.0
            )
            result[label] = Metrics(
                accuracy=overall_acc,
                precision=precision,
                recall=recall,
                f1=f1,
                support=support,
            )
        return result

    @staticmethod
    def macro_f1(truth: Sequence[str], pred: Sequence[str]) -> float:
        """Unweighted mean of per-label F1 (0.0 for empty input)."""
        per = Evaluator.per_label(truth, pred)
        if not per:
            return 0.0
        return sum(m.f1 for m in per.values()) / len(per)

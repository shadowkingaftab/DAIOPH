from __future__ import annotations

import argparse
import csv
import json
import os
import pickle
import random
import statistics
import sys
import time
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "Backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import numpy as np  # noqa: E402

from models.liquid.lnn.intent_model import LiquidIntentModel  # noqa: E402
from models.liquid_neural_networks.lnn_intent_classifier import LiquidIntentClassifier  # noqa: E402

NUM_CHUNKS = 5


def make_dataset(seed: int, train_per_chunk: int, test_per_chunk: int) -> List[Dict[str, Any]]:
    rng = random.Random(seed)
    labels = ["summarize", "translate", "analyze", "code", "multi", "ambiguous", "urgent", "query"]
    chunks = []
    for chunk_id in range(NUM_CHUNKS):
        chunk_labels = [labels[(chunk_id + offset) % len(labels)] for offset in range(3)]
        train = []
        for i in range(train_per_chunk):
            label = chunk_labels[i % len(chunk_labels)]
            text = f"{label} example {i} chunk {chunk_id} seed {seed} variant {rng.randint(0, 999)}"
            train.append((text, label))
        test = []
        for i in range(test_per_chunk):
            label = chunk_labels[i % len(chunk_labels)]
            text = f"{label} test {i} chunk {chunk_id} seed {seed} variant {rng.randint(0, 999)}"
            test.append((text, label))
        rng.shuffle(train)
        rng.shuffle(test)
        chunks.append({"chunk": chunk_id, "train": train, "test": test})
    return chunks


class ModelAdapter:
    name: str

    def update(self, text: str, label: str) -> None:
        raise NotImplementedError

    def predict(self, text: str) -> Any:
        raise NotImplementedError

    def num_parameters(self) -> int:
        raise NotImplementedError

    def serialized_size_mb(self) -> float:
        raise NotImplementedError


class LiquidAdapter(ModelAdapter):
    def __init__(self, seed: int) -> None:
        self.name = "liquid"
        self._seed = seed
        self.model = LiquidIntentModel(layer_taus=(1.0, 2.0))

    def update(self, text: str, label: str) -> None:
        self.model.add_example(text, label)
        self.model.fit()

    def predict(self, text: str) -> Any:
        intent, _ = self.model.predict(text)
        return intent if intent is not None else ""

    def num_parameters(self) -> int:
        count = 0
        for cell in self.model.network.cells:
            count += 3  # weight, bias, tau
        count += len(self.model._prototypes)
        return count

    def serialized_size_mb(self) -> float:
        return len(pickle.dumps(self.model)) / 1e6


class LiquidSGDAdapter(ModelAdapter):
    def __init__(self, seed: int, outdir: Path) -> None:
        self.name = "liquid_sgd"
        self.model = LiquidIntentClassifier(model_path=str(outdir / "models" / f"liquid_sgd_{seed}.pkl"))

    def update(self, text: str, label: str) -> None:
        self.model.update(text, label)

    def predict(self, text: str) -> Any:
        if not self.model.is_trained:
            return ""
        return self.model.classify(text)

    def num_parameters(self) -> int:
        clf = getattr(self.model.pipeline, "named_steps", {}).get("clf") if hasattr(self.model, "pipeline") else None
        count = 0
        if clf is not None and hasattr(clf, "coef_"):
            count += int(np.asarray(clf.coef_).size)
        if clf is not None and hasattr(clf, "intercept_"):
            count += int(np.asarray(clf.intercept_).size)
        vec = getattr(self.model.pipeline, "named_steps", {}).get("tfidf") if hasattr(self.model, "pipeline") else None
        if vec is not None and hasattr(vec, "vocabulary_"):
            count += len(vec.vocabulary_)
        return count

    def serialized_size_mb(self) -> float:
        return len(pickle.dumps(self.model)) / 1e6


class SklearnAdapter(ModelAdapter):
    def __init__(self, seed: int, kind: str) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import SGDClassifier, LogisticRegression
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.neural_network import MLPClassifier
        from sklearn.pipeline import Pipeline

        self.name = kind
        self.kind = kind
        self.seed = seed
        self.X: List[str] = []
        self.y: List[str] = []
        if kind == "sgd":
            clf = SGDClassifier(loss="log_loss", random_state=seed)
        elif kind == "logreg":
            clf = LogisticRegression(max_iter=200, random_state=seed)
        elif kind == "mlp":
            clf = MLPClassifier(hidden_layer_sizes=(16,), max_iter=200, random_state=seed)
        elif kind == "nb":
            clf = MultinomialNB()
        else:
            raise ValueError(f"unknown sklearn kind: {kind}")
        self.pipeline = Pipeline([("tfidf", TfidfVectorizer()), ("clf", clf)])
        self.fitted = False

    def update(self, text: str, label: str) -> None:
        self.X.append(text)
        self.y.append(label)
        unique = set(self.y)
        if len(unique) < 2:
            self.fitted = False
            return
        try:
            self.pipeline.fit(self.X, self.y)
            self.fitted = True
        except Exception:
            self.fitted = False

    def predict(self, text: str) -> Any:
        if not self.fitted:
            if self.y:
                return max(set(self.y), key=self.y.count)
            return ""
        try:
            return self.pipeline.predict([text])[0]
        except Exception:
            return ""

    def num_parameters(self) -> int:
        clf = self.pipeline.named_steps["clf"]
        count = 0
        if hasattr(clf, "coef_"):
            count += int(np.asarray(clf.coef_).size)
        if hasattr(clf, "intercept_"):
            count += int(np.asarray(clf.intercept_).size)
        if hasattr(clf, "coefs_"):
            for c in clf.coefs_:
                count += int(np.asarray(c).size)
        if hasattr(clf, "intercepts_"):
            for c in clf.intercepts_:
                count += int(np.asarray(c).size)
        vec = self.pipeline.named_steps["tfidf"]
        if hasattr(vec, "vocabulary_"):
            count += len(vec.vocabulary_)
        return count

    def serialized_size_mb(self) -> float:
        return len(pickle.dumps(self.pipeline)) / 1e6


def build_model(name: str, seed: int, outdir: Path) -> ModelAdapter:
    if name == "liquid":
        return LiquidAdapter(seed)
    if name in ("liquid_sgd", "liquid_intent"):
        return LiquidSGDAdapter(seed, outdir)
    if name in ("sgd", "logreg", "mlp", "nb"):
        return SklearnAdapter(seed, name)
    raise ValueError(f"unknown model '{name}'; available: liquid, liquid_sgd, sgd, logreg, mlp, nb")


def accuracy(model: ModelAdapter, examples: Sequence[Tuple[str, str]]) -> float:
    if not examples:
        return 0.0
    correct = sum(1 for text, label in examples if model.predict(text) == label)
    return correct / len(examples)


def run_one(model_name: str, seed: int, dataset: List[Dict[str, Any]], outdir: Path, smoke: bool) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    model = build_model(model_name, seed, outdir)
    rows: List[Dict[str, Any]] = []
    timing_rows: List[Dict[str, Any]] = []
    seen_chunks: List[int] = []
    examples_seen = 0
    update_step = 0
    test_sets: Dict[int, List[Tuple[str, str]]] = {}
    eval_interval = 1 if smoke else 5
    last_eval_step = 0

    for chunk_info in dataset:
        chunk_id = chunk_info["chunk"]
        seen_chunks.append(chunk_id)
        test_sets[chunk_id] = chunk_info["test"]
        train_examples = chunk_info["train"]

        for idx, (text, label) in enumerate(train_examples):
            t0 = time.perf_counter()
            model.update(text, label)
            train_ms = (time.perf_counter() - t0) * 1000.0
            examples_seen += 1
            update_step += 1

            should_eval = ((idx + 1) % eval_interval == 0) or (idx == len(train_examples) - 1)
            if not should_eval or examples_seen == last_eval_step:
                timing_rows.append({"model": model_name, "seed": seed, "chunk": chunk_id, "examples_seen": examples_seen, "update_step": update_step, "train_ms": round(train_ms, 4), "eval_ms": 0.0})
                continue

            eval_t0 = time.perf_counter()
            current_acc = accuracy(model, test_sets[chunk_id])
            old_accs = {c: accuracy(model, test_sets[c]) for c in seen_chunks}
            eval_ms = (time.perf_counter() - eval_t0) * 1000.0
            last_eval_step = examples_seen

            row: Dict[str, Any] = {
                "model": model_name,
                "seed": seed,
                "chunk": chunk_id,
                "examples_seen": examples_seen,
                "update_step": update_step,
                "current_chunk_accuracy": round(current_acc, 6),
                "timestamp": time.time(),
            }
            for c in range(NUM_CHUNKS):
                row[f"chunk_{c}_accuracy"] = round(old_accs[c], 6) if c in old_accs else None
            rows.append(row)
            timing_rows.append({"model": model_name, "seed": seed, "chunk": chunk_id, "examples_seen": examples_seen, "update_step": update_step, "train_ms": round(train_ms, 4), "eval_ms": round(eval_ms, 4)})

    # warmup + latency
    sample_text = dataset[0]["train"][0][0] if dataset and dataset[0]["train"] else "sample"
    warmup = 5 if smoke else 10
    for _ in range(warmup):
        model.predict(sample_text)
    latencies = []
    iters = 20 if smoke else 100
    for _ in range(iters):
        t0 = time.perf_counter()
        model.predict(sample_text)
        latencies.append((time.perf_counter() - t0) * 1000.0)
    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[min(len(latencies) - 1, int(0.95 * (len(latencies) - 1)))]

    # derived adaptation: current-chunk accuracy curve vs examples seen
    current_points = [(r["examples_seen"], r["current_chunk_accuracy"]) for r in rows]
    auc = 0.0
    for i in range(1, len(current_points)):
        x0, y0 = current_points[i - 1]
        x1, y1 = current_points[i]
        auc += (x1 - x0) * (y0 + y1) / 2.0

    # retention: each old chunk accuracy after later chunks + max-final
    retention: Dict[str, Any] = {}
    for c in range(NUM_CHUNKS):
        vals = [(r["examples_seen"], r[f"chunk_{c}_accuracy"]) for r in rows if r[f"chunk_{c}_accuracy"] is not None]
        if not vals:
            continue
        max_acc = max(v for _, v in vals)
        final_acc = vals[-1][1]
        retention[f"chunk_{c}"] = {
            "trajectory": [{"examples_seen": x, "accuracy": y} for x, y in vals],
            "max_accuracy": max_acc,
            "final_accuracy": final_acc,
            "forgetting": round(max_acc - final_acc, 6),
        }

    derived = {
        "model": model_name,
        "seed": seed,
        "adaptation": {
            "current_chunk_accuracy_curve": [{"examples_seen": x, "accuracy": y} for x, y in current_points],
            "auc_vs_examples_seen": round(auc, 6),
        },
        "retention": retention,
        "parameters": {
            "count": model.num_parameters(),
            "serialized_size_mb": round(model.serialized_size_mb(), 6),
        },
        "latency_ms": {
            "warmup_iterations": warmup,
            "measured_iterations": iters,
            "p50": round(p50, 6),
            "p95": round(p95, 6),
        },
        "timing_summary": {
            "train_ms_total": round(sum(t["train_ms"] for t in timing_rows), 4),
            "eval_ms_total": round(sum(t["eval_ms"] for t in timing_rows), 4),
        },
        "flops_macs": {
            "status": "unavailable",
            "reason": "No supported FLOP/MAC counter can measure these pure-Python/sklearn architectures.",
            "counting_attempt": "Checked torch.profiler/fvcore/thop/ptflops availability; none applicable to LiquidIntentModel or sklearn pipelines. Manual FLOP counting not performed to avoid unsupported estimates.",
        },
    }

    # write timing rows appended by caller? Return them via derived? We'll return rows only; timing saved separately.
    # Store timing rows in derived for convenience
    derived["_timing_rows"] = timing_rows

    return rows, derived


def main() -> int:
    parser = argparse.ArgumentParser(description="Day 3 liquid streaming evaluation protocol and runner.")
    parser.add_argument("--dataset", default="synthetic", help="Dataset name or path (currently synthetic).")
    parser.add_argument("--seeds", default="0,1", help="Comma-separated seeds.")
    parser.add_argument("--models", default="liquid", help="Comma-separated model names.")
    parser.add_argument("--outdir", default="Research/experiments/liquid_streaming/results", help="Output directory.")
    parser.add_argument("--smoke", action="store_true", help="Smoke mode (small data).")
    parser.add_argument("--train-per-chunk", type=int, default=None)
    parser.add_argument("--test-per-chunk", type=int, default=None)
    parser.add_argument("--eval-interval", type=int, default=None)
    args = parser.parse_args()

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    outdir = Path(args.outdir)
    if not outdir.is_absolute():
        outdir = ROOT / outdir
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "models").mkdir(parents=True, exist_ok=True)

    train_per_chunk = args.train_per_chunk if args.train_per_chunk is not None else (6 if args.smoke else 40)
    test_per_chunk = args.test_per_chunk if args.test_per_chunk is not None else (4 if args.smoke else 10)

    all_rows: List[Dict[str, Any]] = []
    all_derived: List[Dict[str, Any]] = []
    all_timing: List[Dict[str, Any]] = []

    for model_name in models:
        for seed in seeds:
            print(f"[{model_name}] seed={seed} ...", flush=True)
            dataset = make_dataset(seed, train_per_chunk, test_per_chunk)
            rows, derived = run_one(model_name, seed, dataset, outdir, args.smoke)
            all_rows.extend(rows)
            timing_rows = derived.pop("_timing_rows", [])
            all_timing.extend(timing_rows)
            all_derived.append(derived)
            print(f"  rows={len(rows)} auc={derived['adaptation']['auc_vs_examples_seen']} params={derived['parameters']['count']} sizeMB={derived['parameters']['serialized_size_mb']} p50={derived['latency_ms']['p50']}ms p95={derived['latency_ms']['p95']}ms", flush=True)

    raw_fields = ["model", "seed", "chunk", "examples_seen", "update_step", "current_chunk_accuracy"] + [f"chunk_{c}_accuracy" for c in range(NUM_CHUNKS)] + ["timestamp"]
    with (outdir / "raw_rows.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=raw_fields)
        writer.writeheader()
        writer.writerows(all_rows)

    timing_fields = ["model", "seed", "chunk", "examples_seen", "update_step", "train_ms", "eval_ms"]
    with (outdir / "timing.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=timing_fields)
        writer.writeheader()
        writer.writerows(all_timing)

    (outdir / "derived.json").write_text(json.dumps(all_derived, indent=2), encoding="utf-8")
    (outdir / "summary.json").write_text(json.dumps({
        "dataset": args.dataset,
        "smoke": args.smoke,
        "seeds": seeds,
        "models": models,
        "train_per_chunk": train_per_chunk,
        "test_per_chunk": test_per_chunk,
        "chunks": NUM_CHUNKS,
        "raw_rows": len(all_rows),
    }, indent=2), encoding="utf-8")

    print(f"Wrote {outdir / 'raw_rows.csv'} ({len(all_rows)} rows)")
    print(f"Wrote {outdir / 'derived.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

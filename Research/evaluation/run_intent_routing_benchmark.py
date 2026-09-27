"""Run the DAIOPH intent-routing benchmark locally.

This measures classifier and routing decisions only.  It never calls Qwen,
Grok, or another inference provider, so all 60 evaluation prompts remain in
the local benchmark process.  The first run may download the classifier model
if it is not already cached by Transformers.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "Backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from classifier import _MODEL_ID, classify_prompt  # noqa: E402
from router import choose_route  # noqa: E402


DEFAULT_DATASET = Path(__file__).with_name("datasets") / "intent_routing_60.jsonl"


def load_cases(dataset: Path) -> list[dict[str, str]]:
    """Load one audited JSON record per prompt."""
    cases: list[dict[str, str]] = []
    for line_number, line in enumerate(dataset.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON at {dataset}:{line_number}: {error}") from error
        required = {"id", "category", "prompt", "expected_intent", "expected_route", "safety_tag"}
        missing = required.difference(case)
        if missing:
            raise ValueError(f"Missing {sorted(missing)} at {dataset}:{line_number}")
        cases.append(case)
    if not cases:
        raise ValueError("The benchmark dataset contains no prompts.")
    return cases


def percent(value: int, total: int) -> float:
    return round((value / total * 100) if total else 0.0, 2)


def percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(round((len(ordered) - 1) * fraction), len(ordered) - 1)
    return round(ordered[index], 2)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# DAIOPH Intent Routing Benchmark",
        "",
        f"- Run time (UTC): {summary['run_metadata']['run_at_utc']}",
        f"- Classifier: `{summary['run_metadata']['classifier_model']}`",
        f"- Explicit routing signals enabled: {summary['run_metadata']['routing_rules_enabled']}",
        f"- Evaluation mode: local classifier and route decision only; no prompt execution.",
        "",
        "## Table V. Intent Routing Accuracy by Prompt Category",
        "",
        "| Category | Prompts | Correct | Accuracy |",
        "|---|---:|---:|---:|",
    ]
    for row in summary["category_results"]:
        lines.append(f"| {row['category']} | {row['prompts']} | {row['route_correct']} | {row['routing_accuracy_percent']:.2f}% |")
    overall = summary["overall"]
    lines.extend(
        [
            f"| Overall | {overall['prompts']} | {overall['route_correct']} | {overall['routing_accuracy_percent']:.2f}% |",
            "",
            "## Supporting Metrics",
            "",
            f"- Intent accuracy: {overall['intent_accuracy_percent']:.2f}% ({overall['intent_correct']}/{overall['prompts']})",
            f"- Mean classification latency: {overall['mean_classification_latency_ms']:.2f} ms",
            f"- P95 classification latency: {overall['p95_classification_latency_ms']:.2f} ms",
            f"- Local-eligible prompts kept local: {overall['local_eligible_local_rate_percent']:.2f}%",
            f"- Risk-route compliance: {overall['risk_route_compliance_percent']:.2f}%",
            "",
            "`Risk-route compliance` measures whether prompts marked urgent, uncertain, or complex received their pre-registered expected route. It does not establish general system safety or output quality.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_diagnosis(path: Path, cases: list[dict[str, str]], records: list[dict[str, Any]]) -> None:
    ids = [case["id"] for case in cases]
    normalized_prompts = [" ".join(case["prompt"].lower().split()) for case in cases]
    duplicate_ids = [item for item, count in Counter(ids).items() if count > 1]
    duplicate_prompts = [item for item, count in Counter(normalized_prompts).items() if count > 1]
    categories = Counter(case["category"] for case in cases)
    intents = Counter(case["expected_intent"] for case in cases)
    routes = Counter(case["expected_route"] for case in cases)
    failures = [record for record in records if record["error"]]
    lines = [
        "# Benchmark Diagnosis",
        "",
        "## Dataset integrity",
        "",
        f"- Prompt count: {len(cases)}",
        f"- Unique prompt IDs: {len(set(ids))}",
        f"- Duplicate IDs: {len(duplicate_ids)}",
        f"- Exact duplicate prompts: {len(duplicate_prompts)}",
        f"- Classifier errors: {len(failures)}",
        "",
        "## Pre-registered distribution",
        "",
        "| Field | Distribution |",
        "|---|---|",
        f"| Categories | {dict(sorted(categories.items()))} |",
        f"| Expected intents | {dict(sorted(intents.items()))} |",
        f"| Expected routes | {dict(sorted(routes.items()))} |",
        "",
        "## Interpretation limits",
        "",
        "- This is a fixed, human-labeled internal benchmark. It supports a claim about these prompts and the recorded environment, not all user requests.",
        "- Routing accuracy measures the decision route, not response correctness, helpfulness, or factuality.",
        "- The benchmark runner does not execute cloud or local models. Output-quality, safety-red-team, and Liquid Neural Transformer adaptation claims require separate experiments.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(cases: list[dict[str, str]], use_routing_rules: bool = True) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] {case['id']} — {case['category']}", flush=True)
        try:
            prediction = classify_prompt(case["prompt"], use_routing_rules=use_routing_rules)
            actual_route = choose_route(prediction["intent_matrix"], case["prompt"])
            error = ""
        except Exception as exc:  # Preserve failure evidence in the results.
            prediction = {"top_intent": "ERROR", "top_confidence": 0.0, "latency_ms": 0.0, "intent_matrix": {}}
            actual_route = "ERROR"
            error = f"{type(exc).__name__}: {exc}"
        records.append(
            {
                **case,
                "predicted_intent": prediction["top_intent"],
                "predicted_confidence": prediction["top_confidence"],
                "actual_route": actual_route,
                "intent_correct": prediction["top_intent"] == case["expected_intent"],
                "route_correct": actual_route == case["expected_route"],
                "classification_latency_ms": prediction["latency_ms"],
                "intent_scores": json.dumps(prediction["intent_matrix"], sort_keys=True),
                "error": error,
            }
        )

    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_category[record["category"]].append(record)
    category_results = []
    for category, group in by_category.items():
        correct = sum(record["route_correct"] for record in group)
        category_results.append(
            {
                "category": category,
                "prompts": len(group),
                "route_correct": correct,
                "routing_accuracy_percent": percent(correct, len(group)),
            }
        )

    total = len(records)
    route_correct = sum(record["route_correct"] for record in records)
    intent_correct = sum(record["intent_correct"] for record in records)
    local_eligible = [record for record in records if record["safety_tag"] == "local_eligible"]
    risk_records = [record for record in records if record["safety_tag"] != "local_eligible"]
    latencies = [float(record["classification_latency_ms"]) for record in records]
    overall = {
        "prompts": total,
        "route_correct": route_correct,
        "routing_accuracy_percent": percent(route_correct, total),
        "intent_correct": intent_correct,
        "intent_accuracy_percent": percent(intent_correct, total),
        "mean_classification_latency_ms": round(statistics.mean(latencies), 2),
        "p95_classification_latency_ms": percentile(latencies, 0.95),
        "local_eligible_local_rate_percent": percent(sum(record["actual_route"] == "ODA" for record in local_eligible), len(local_eligible)),
        "risk_route_compliance_percent": percent(sum(record["route_correct"] for record in risk_records), len(risk_records)),
        "actual_route_distribution": dict(Counter(record["actual_route"] for record in records)),
    }
    summary = {
        "run_metadata": {
            "run_at_utc": datetime.now(timezone.utc).isoformat(),
            "classifier_model": _MODEL_ID,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "benchmark_mode": "local decision-only",
            "routing_rules_enabled": use_routing_rules,
        },
        "category_results": category_results,
        "overall": overall,
    }
    return records, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local DAIOPH routing benchmark.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).with_name("results"))
    parser.add_argument("--limit", type=int, default=None, help="Run the first N prompts for a smoke check.")
    parser.add_argument(
        "--zero-shot-baseline",
        action="store_true",
        help="Disable DAIOPH's explicit routing signals for a zero-shot baseline comparison.",
    )
    args = parser.parse_args()

    cases = load_cases(args.dataset)
    if args.limit is not None:
        cases = cases[: args.limit]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records, summary = run(cases, use_routing_rules=not args.zero_shot_baseline)
    fields = [
        "id", "category", "prompt", "expected_intent", "predicted_intent", "predicted_confidence",
        "expected_route", "actual_route", "intent_correct", "route_correct", "safety_tag",
        "classification_latency_ms", "intent_scores", "error",
    ]
    write_csv(args.output_dir / "routing_results.csv", records, fields)
    write_csv(
        args.output_dir / "route_confusion_matrix.csv",
        [
            {"expected_route": expected, "actual_route": actual, "count": count}
            for (expected, actual), count in sorted(Counter((r["expected_route"], r["actual_route"]) for r in records).items())
        ],
        ["expected_route", "actual_route", "count"],
    )
    (args.output_dir / "routing_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_markdown(args.output_dir / "routing_table.md", summary)
    write_diagnosis(args.output_dir / "diagnosis_report.md", cases, records)
    print("\nCompleted. Open these local artifacts:")
    for name in ("routing_table.md", "routing_results.csv", "route_confusion_matrix.csv", "diagnosis_report.md"):
        print(args.output_dir / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Measure strict end-to-end DAIOPH route execution latency.

This runner intentionally bypasses route fallbacks: each named configuration
must use the named provider, so an unavailable provider is reported as a
failure rather than being substituted with a different route.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "Backend"
sys.path.insert(0, str(BACKEND))

from gemini_cloud import DEFAULT_MODEL, is_api_key_set, run_gemini  # noqa: E402
from qwen_oda import (  # noqa: E402
    MODEL_PATH,
    MODEL_SIZE_MB,
    N_BATCH,
    N_CTX,
    N_GPU_LAYERS,
    N_THREADS,
    QUANT_LEVEL,
    _cached_run,
    is_llm_available,
    is_model_downloaded,
    run_qwen,
)

DEFAULT_DATASET = Path(__file__).with_name("datasets") / "intent_routing_60.jsonl"
DEFAULT_OUTPUT = Path(__file__).with_name("results") / "end_to_end_latency"
PROMPT_COUNT = 30
ITERATIONS = 30
WARMUPS = 5


def load_prompts(path: Path) -> list[dict[str, str]]:
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(cases) < PROMPT_COUNT:
        raise ValueError(f"Need at least {PROMPT_COUNT} prompts; found {len(cases)}.")
    return cases[:PROMPT_COUNT]


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * fraction
    lower, upper = math.floor(index), math.ceil(index)
    return values[lower] if lower == upper else values[lower] + (values[upper] - values[lower]) * (index - lower)


def success_output(output: str) -> bool:
    return bool(output and not output.startswith(("❌", "⚠️", "Qwen unavailable:", "Qwen inference error:")))


def is_quota_error(output: str) -> bool:
    normalized = output.lower()
    return "429" in normalized or "resource_exhausted" in normalized or "quota exceeded" in normalized


def local_execute(prompt: str) -> tuple[str, str]:
    _cached_run.cache_clear()
    return run_qwen(prompt), "Qwen2-0.5B-Instruct-GGUF"


def cloud_execute(prompt: str) -> tuple[str, str]:
    return run_gemini(prompt), f"Google Gemini/{DEFAULT_MODEL}"


def hybrid_execute(prompt: str) -> tuple[str, str]:
    _cached_run.cache_clear()
    edge = run_qwen(f"Handle the first part of this task concisely: {prompt}")
    if not success_output(edge):
        return edge, "Qwen2-0.5B-Instruct-GGUF + Google Gemini"
    cloud = run_gemini(f"Handle the second part of this task in detail: {prompt}")
    if not success_output(cloud):
        return cloud, "Qwen2-0.5B-Instruct-GGUF + Google Gemini"
    return f"[Edge]\n{edge}\n\n[Cloud]\n{cloud}", "Qwen2-0.5B-Instruct-GGUF + Google Gemini"


def preflight(configuration: str) -> str | None:
    if configuration in {"local-only", "hybrid"}:
        if not is_llm_available():
            return "llama-cpp-python is unavailable"
        if not is_model_downloaded() or Path(MODEL_PATH).stat().st_size < MODEL_SIZE_MB * 1024 * 1024:
            return f"Local Qwen model is incomplete or not installed at {MODEL_PATH}"
    if configuration in {"cloud-only", "hybrid"} and not is_api_key_set():
        return "GEMINI_API_KEY is not configured"
    return None


def run_configuration(configuration: str, prompts: list[dict[str, str]], execute: Callable[[str], tuple[str, str]], start_prompt: int = 1, iterations: int = ITERATIONS, warmups: int = WARMUPS, prompt_limit: int | None = None) -> list[dict[str, Any]]:
    unavailable = preflight(configuration)
    records: list[dict[str, Any]] = []
    if unavailable:
        print(f"[{configuration}] unavailable: {unavailable}", flush=True)
        return records

    for warmup in range(warmups):
        output, _ = execute(prompts[warmup % len(prompts)]["prompt"])
        if is_quota_error(output):
            print(f"[{configuration}] stopping: provider quota/rate limit returned HTTP 429 during warmup", flush=True)
            return records

    for case_index, case in enumerate(prompts[start_prompt - 1 :], start=start_prompt):
        if prompt_limit is not None and case_index >= start_prompt + prompt_limit:
            break
        print(f"[{configuration}] prompt {case_index}/{len(prompts)}: {case['id']}", flush=True)
        for iteration in range(1, iterations + 1):
            started_at = datetime.now(timezone.utc)
            start = time.perf_counter_ns()
            try:
                output, model = execute(case["prompt"])
                error = "" if success_output(output) else output[:1000]
                success = not error
            except Exception as exc:
                output = ""
                model, success, error = None, False, f"{type(exc).__name__}: {exc}"
            elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
            ended_at = datetime.now(timezone.utc)
            records.append({"prompt_id": case["id"], "configuration": configuration, "iteration": iteration, "start_time_utc": started_at.isoformat(), "end_time_utc": ended_at.isoformat(), "latency_ms": round(elapsed_ms, 3), "success": success, "error": error, "selected_route_model": model})
            if is_quota_error(output):
                print(f"[{configuration}] stopping: provider quota/rate limit returned HTTP 429", flush=True)
                return records
    return records


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [record["latency_ms"] for record in records if record["success"]]
    return {"total_executions": len(records), "successful_executions": len(successful), "failed_executions": len(records) - len(successful), "mean_latency_ms": round(statistics.mean(successful), 3) if successful else None, "median_latency_ms": round(statistics.median(successful), 3) if successful else None, "standard_deviation_ms": round(statistics.stdev(successful), 3) if len(successful) > 1 else (0.0 if successful else None), "p95_latency_ms": round(percentile(successful, 0.95), 3) if successful else None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--configuration", choices=("local-only", "cloud-only", "hybrid"), help="Run only one configuration.")
    parser.add_argument("--start-prompt", type=int, default=1, help="Resume at this 1-based prompt index (the prompt itself runs from iteration 1).")
    parser.add_argument("--iterations", type=int, default=ITERATIONS, help=f"Measured iterations per prompt (default: {ITERATIONS}).")
    parser.add_argument("--prompt-limit", type=int, help="Run at most this many prompts from --start-prompt.")
    parser.add_argument("--warmups", type=int, default=WARMUPS, help=f"Warmup calls per configuration (default: {WARMUPS}).")
    parser.add_argument("--max-api-requests", type=int, default=20, help="Refuse cloud runs whose worst-case API call count exceeds this cap (default: 20).")
    args = parser.parse_args()
    prompts = load_prompts(args.dataset)
    if not 1 <= args.start_prompt <= len(prompts):
        parser.error(f"--start-prompt must be between 1 and {len(prompts)}")
    if args.iterations < 1:
        parser.error("--iterations must be at least 1")
    if args.warmups < 0:
        parser.error("--warmups cannot be negative")
    if args.prompt_limit is not None and args.prompt_limit < 1:
        parser.error("--prompt-limit must be at least 1")
    if args.max_api_requests < 0:
        parser.error("--max-api-requests cannot be negative")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    configurations = [("local-only", local_execute), ("cloud-only", cloud_execute), ("hybrid", hybrid_execute)]
    selected_configurations = [item for item in configurations if args.configuration is None or item[0] == args.configuration]
    selected_prompt_count = len(prompts) - args.start_prompt + 1
    if args.prompt_limit is not None:
        selected_prompt_count = min(selected_prompt_count, args.prompt_limit)
    api_configurations = {"cloud-only", "hybrid"}
    worst_case_api_requests = sum(args.warmups + selected_prompt_count * args.iterations for name, _ in selected_configurations if name in api_configurations)
    if worst_case_api_requests > args.max_api_requests:
        parser.error(f"This run could make up to {worst_case_api_requests} cloud API requests, above --max-api-requests={args.max_api_requests}. Reduce prompts, iterations, or warmups.")
    records = [record for name, execute in selected_configurations for record in run_configuration(name, prompts, execute, args.start_prompt, args.iterations, args.warmups, args.prompt_limit)]
    fields = ["prompt_id", "configuration", "iteration", "start_time_utc", "end_time_utc", "latency_ms", "success", "error", "selected_route_model"]
    with (args.output_dir / "raw_measurements.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    availability = {name: preflight(name) or "available" for name, _ in configurations}
    summary = {"run_metadata": {"run_at_utc": datetime.now(timezone.utc).isoformat(), "prompt_count": selected_prompt_count, "prompt_start_index": args.start_prompt, "configurations_run": [name for name, _ in selected_configurations], "measured_iterations_per_prompt": args.iterations, "warmups_per_configuration": args.warmups, "worst_case_api_requests": worst_case_api_requests, "api_request_cap": args.max_api_requests, "python": sys.version.split()[0], "platform": platform.platform(), "local_configuration": {"model": "Qwen2-0.5B-Instruct-GGUF", "quantization": QUANT_LEVEL, "threads": N_THREADS, "batch": N_BATCH, "context": N_CTX, "gpu_layers": N_GPU_LAYERS}, "cloud_configuration": {"provider": "Google Gemini", "model": DEFAULT_MODEL}, "hybrid_configuration": "Qwen local edge stage followed by Google Gemini cloud stage; no provider fallback"}, "availability": availability, "results": {name: summarize([record for record in records if record["configuration"] == name]) for name, _ in configurations}}
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["results"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

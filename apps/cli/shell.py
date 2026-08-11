"""Interactive shell for the DAIOPH CLI."""

import sys
from typing import Optional


def run_interactive_shell() -> int:
    """Run an interactive chat shell.

    Returns:
        int: Exit code.
    """
    print("=" * 60)
    print("DAIOPH Interactive Shell")
    print("Type 'exit', 'quit', or Ctrl+C to leave.")
    print("=" * 60)

    try:
        from core.hybrid_orchestrator import HybridOrchestrator

        orch = HybridOrchestrator(
            distilbert_path="distilbert-base-uncased",
            qwen_path="models/qwen2-0_5b-instruct-q4_k_m.gguf",
            grok_api_key=None,
        )
    except Exception as e:
        print(f"[DAIOPH] Failed to initialize orchestrator: {e}", file=sys.stderr)
        return 1

    route = "Hybrid"

    while True:
        try:
            prompt = input(f"\n[{route}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[DAIOPH] Goodbye!")
            return 0

        if not prompt:
            continue
        if prompt.lower() in ("exit", "quit"):
            print("[DAIOPH] Goodbye!")
            return 0
        if prompt.lower() == "route":
            route = input("Route (ODA/Hybrid/Cloud): ").strip().capitalize()
            if route not in ("ODA", "Hybrid", "Cloud"):
                route = "Hybrid"
            continue

        try:
            dag, results = orch.execute(prompt, None, route)
            print("\n" + results.get("final_output", "No output."))
        except Exception as e:
            print(f"[DAIOPH] Error: {e}", file=sys.stderr)
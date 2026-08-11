"""DAIOPH CLI command implementations."""

import argparse
import json
import sys
from typing import Optional

from apps.cli.formatter import format_table, format_json


def cmd_help(parser: argparse.ArgumentParser) -> None:
    """Show help."""
    parser.print_help()


def cmd_chat(args: argparse.Namespace) -> int:
    """Send a chat message or start interactive mode."""
    from apps.cli.shell import run_interactive_shell

    if args.interactive:
        return run_interactive_shell()
    if not args.message:
        print("[DAIOPH] Please provide a message or use --interactive for chat mode.")
        return 1

    try:
        from core.hybrid_orchestrator import HybridOrchestrator

        orch = HybridOrchestrator(
            distilbert_path="distilbert-base-uncased",
            qwen_path="models/qwen2-0_5b-instruct-q4_k_m.gguf",
            grok_api_key=None,
        )
        dag, results = orch.execute(args.message, None, args.route)
        print("\n" + "=" * 60)
        print("RESULT:")
        print("=" * 60)
        print(results.get("final_output", "No output."))
        print("=" * 60)
        times = results.get("times", {})
        print(f"\nEdge AI: {times.get('edge_ai', '?')}s | "
              f"Traditional: {times.get('traditional', '?')}s | "
              f"Savings: {times.get('savings_percent', '?')}%")
        return 0
    except Exception as e:
        print(f"[DAIOPH] Failed to run chat: {e}", file=sys.stderr)
        return 1


def cmd_models() -> int:
    """List available models."""
    models = [
        {"id": "qwen2-0.5b", "name": "Qwen2-0.5B-Instruct", "type": "local", "status": "available"},
        {"id": "distilbert", "name": "DistilBERT-base-uncased", "type": "local", "status": "available"},
        {"id": "grok", "name": "xAI Grok", "type": "remote", "status": "available"},
    ]
    print(format_table(
        headers=["ID", "Name", "Type", "Status"],
        rows=[[m["id"], m["name"], m["type"], m["status"]] for m in models],
    ))
    return 0


def cmd_status() -> int:
    """Show system status."""
    try:
        import psutil

        status = {
            "cpu": f"{psutil.cpu_percent()}%",
            "ram": f"{psutil.virtual_memory().percent}%",
            "cores": psutil.cpu_count(),
            "status": "ok",
        }
    except ImportError:
        status = {"status": "unknown", "note": "psutil not available"}

    print(format_json(status))
    return 0


def cmd_train(args: argparse.Namespace) -> int:
    """Train the intent classifier."""
    try:
        import subprocess

        cmd = [
            sys.executable,
            "training/train_classifier.py",
            "--epochs",
            str(args.epochs),
        ]
        if args.eval:
            cmd.append("--eval")

        print(f"[DAIOPH] Training classifier with {args.epochs} epochs...")
        result = subprocess.run(cmd, cwd=".", capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return result.returncode
        return 0
    except Exception as e:  # pragma: no cover
        print(f"[DAIOPH] Training failed: {e}", file=sys.stderr)
        return 1


def cmd_memory(args: argparse.Namespace) -> int:
    """Browse memory entries."""
    try:
        from memory.short_term_memory import ShortTermMemory

        mem = ShortTermMemory()
        entries = mem.get_recent(args.limit)
        if not entries:
            print("[DAIOPH] No memory entries found.")
            return 0

        rows = [[e[0], e[1][:50] + ("..." if len(e[1]) > 50 else "")] for e in entries]
        print(format_table(headers=["Intent", "Prompt"], rows=rows))
        return 0
    except Exception as e:  # pragma: no cover
        print(f"[DAIOPH] Memory access failed: {e}", file=sys.stderr)
        return 1
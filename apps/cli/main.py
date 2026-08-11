"""DAIOPH CLI - Command Line Interface entry point."""

import argparse
import sys
from typing import List, Optional

from apps.cli.commands import (
    cmd_chat,
    cmd_models,
    cmd_status,
    cmd_train,
    cmd_memory,
    cmd_help,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="daiph",
        description="DAIOPH Edge AI Command Line Interface",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # chat
    chat_parser = subparsers.add_parser("chat", help="Send a message to DAIOPH")
    chat_parser.add_argument("message", nargs="?", help="Message to send")
    chat_parser.add_argument("-r", "--route", choices=["ODA", "Hybrid", "Cloud"], default="Hybrid")
    chat_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive chat mode")

    # models
    subparsers.add_parser("models", help="List available models")

    # status
    subparsers.add_parser("status", help="Show system status")

    # train
    train_parser = subparsers.add_parser("train", help="Train the intent classifier")
    train_parser.add_argument("--epochs", type=int, default=5)
    train_parser.add_argument("--eval", action="store_true")

    # memory
    memory_parser = subparsers.add_parser("memory", help="Browse memory")
    memory_parser.add_argument("--type", help="Filter by memory type")
    memory_parser.add_argument("--limit", type=int, default=20)

    # help
    subparsers.add_parser("help", help="Show help")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command or args.command == "help":
        cmd_help(parser)
        return 0

    try:
        if args.command == "chat":
            return cmd_chat(args)
        if args.command == "models":
            return cmd_models()
        if args.command == "status":
            return cmd_status()
        if args.command == "train":
            return cmd_train(args)
        if args.command == "memory":
            return cmd_memory(args)
    except Exception as e:  # pragma: no cover
        print(f"[DAIOPH] Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
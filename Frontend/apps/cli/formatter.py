"""Output formatting utilities for the DAIOPH CLI."""

import json
from typing import Any, List, Sequence


def format_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Format data as an ASCII table.

    Args:
        headers: Column headers.
        rows: Table rows.

    Returns:
        str: Formatted table string.
    """
    if not headers:
        return ""

    # Calculate column widths
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))

    # Build header
    header_line = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in widths)

    # Build rows
    lines = [header_line, separator]
    for row in rows:
        line = " | ".join(
            str(cell).ljust(widths[i]) if i < len(widths) else str(cell)
            for i, cell in enumerate(row)
        )
        lines.append(line)

    return "\n".join(lines)


def format_json(data: Any) -> str:
    """Format data as pretty-printed JSON.

    Args:
        data: Data to serialize.

    Returns:
        str: Pretty-printed JSON string.
    """
    return json.dumps(data, indent=2, default=str)


def format_key_value(data: dict) -> str:
    """Format a dict as aligned key-value pairs.

    Args:
        data: Dictionary to format.

    Returns:
        str: Formatted key-value string.
    """
    if not data:
        return ""
    width = max(len(str(k)) for k in data.keys())
    return "\n".join(f"{str(k).ljust(width)} : {v}" for k, v in data.items())
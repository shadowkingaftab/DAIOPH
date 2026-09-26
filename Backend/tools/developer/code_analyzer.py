"""Static code analysis (stdlib tokenize; no external linters)."""

from __future__ import annotations

import ast
import tokenize
from io import StringIO
from typing import Any, Dict, List

from tools.registry.tool_schema import ToolSchema

__all__ = ["analyze_code", "dev_analyzer"]


def analyze_code(source: str) -> Dict[str, Any]:
    """Return function/class counts and a token count for *source*."""
    try:
        tree = ast.parse(source)
        functions = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
        classes = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    except SyntaxError as exc:
        return {"valid": False, "error": str(exc)}
    tokens = list(tokenize.generate_tokens(StringIO(source).readline))
    return {
        "valid": True,
        "functions": functions,
        "classes": classes,
        "token_count": len(tokens),
    }


dev_analyzer = ToolSchema(
    name="dev_analyzer",
    description="Analyze Python source: functions, classes, token count",
    fn=analyze_code,
    params={"source": str},
)

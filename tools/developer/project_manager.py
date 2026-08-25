"""Project scaffolding tool (creates files; approval-gated)."""

from __future__ import annotations

from pathlib import Path
from typing import List

from tools.registry.tool_schema import ToolSchema

__all__ = ["scaffold_project", "dev_project"]


def scaffold_project(root: str, name: str) -> List[str]:
    """Create a minimal Python package skeleton under *root*."""
    base = Path(root) / name
    (base / "src" / name).mkdir(parents=True, exist_ok=True)
    (base / "tests").mkdir(parents=True, exist_ok=True)
    init_text = "Package " + name + "."
    (base / "src" / name / "__init__.py").write_text(
        init_text, encoding="utf-8"
    )
    pyproject = "[project]" + chr(10) + 'name = "' + name + '"' + chr(10) + 'version = "0.1.0"' + chr(10)
    (base / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    return [str(p) for p in sorted(base.rglob("*")) if p.is_file()]


dev_project = ToolSchema(
    name="dev_project",
    description="Scaffold a minimal Python package (destructive; approval)",
    fn=scaffold_project,
    params={"root": str, "name": str},
    destructive=True,
)
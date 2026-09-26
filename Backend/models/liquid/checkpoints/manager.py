"""Checkpoint manager for liquid models (JSON, injected persistence)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

__all__ = ["CheckpointManager"]

Writer = Callable[[str, str], None]
Loader = Callable[[str], str]


class CheckpointManager:
    """Saves/loads model state dicts with format-version metadata.

    Persistence is pluggable: pass a directory (file backend) or
    writer/loader callables (in-memory backend for tests).
    """

    FORMAT_VERSION = 1

    def __init__(
        self,
        directory: Optional[Path] = None,
        writer: Optional[Writer] = None,
        loader: Optional[Loader] = None,
    ) -> None:
        if directory is None and (writer is None or loader is None):
            raise ValueError(
                "provide a directory or both writer and loader callables"
            )
        self._directory = Path(directory) if directory else None
        self._writer = writer
        self._loader = loader

    def _key(self, name: str) -> str:
        return f"{name}.liquid.json"

    def save(self, name: str, state: Dict[str, Any]) -> str:
        """Persist *state* under *name*; returns the storage key."""
        payload = json.dumps(
            {
                "format_version": self.FORMAT_VERSION,
                "name": name,
                "state": state,
            },
            sort_keys=True,
        )
        key = self._key(name)
        if self._writer is not None:
            self._writer(key, payload)
        else:
            assert self._directory is not None
            self._directory.mkdir(parents=True, exist_ok=True)
            (self._directory / key).write_text(payload, encoding="utf-8")
        return key

    def load(self, name: str) -> Dict[str, Any]:
        """Load state; raises FileNotFoundError when absent."""
        key = self._key(name)
        if self._loader is not None:
            raw = self._loader(key)
        else:
            assert self._directory is not None
            path = self._directory / key
            if not path.is_file():
                raise FileNotFoundError(f"no checkpoint: {key}")
            raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        version = data.get("format_version")
        if version != self.FORMAT_VERSION:
            raise ValueError(f"unsupported checkpoint format: {version!r}")
        return data["state"]

    def exists(self, name: str) -> bool:
        """True when the checkpoint loads cleanly."""
        try:
            self.load(name)
            return True
        except (FileNotFoundError, ValueError, KeyError):
            return False

    def list_checkpoints(self) -> List[str]:
        """Checkpoint names present (directory backend only)."""
        if self._directory is None or not self._directory.is_dir():
            return []
        names: List[str] = []
        for path in sorted(self._directory.iterdir()):
            if path.name.endswith(".liquid.json"):
                names.append(path.name[: -len(".liquid.json")])
        return names

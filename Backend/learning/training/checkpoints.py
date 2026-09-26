"""Training checkpoints persisted as JSON via an injected store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

__all__ = ["CheckpointStore"]

Writer = Callable[[str, str], None]
Loader = Callable[[str], str]


class CheckpointStore:
    """Named, versioned checkpoints with pluggable persistence.

    The default backend writes JSON files under a directory; tests can
    inject in-memory ``writer``/``loader`` callables instead.
    """

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

    def _key(self, name: str, version: int) -> str:
        return f"{name}.v{version}.json"

    def save(self, name: str, state: Dict[str, Any], version: int = 1) -> str:
        """Persist *state* under *name*/*version*; returns the storage key."""
        if version < 1:
            raise ValueError("version must be >= 1")
        payload = json.dumps(
            {"name": name, "version": version, "state": state},
            sort_keys=True,
        )
        key = self._key(name, version)
        if self._writer is not None:
            self._writer(key, payload)
        else:
            assert self._directory is not None
            self._directory.mkdir(parents=True, exist_ok=True)
            (self._directory / key).write_text(payload, encoding="utf-8")
        return key

    def load(self, name: str, version: int = 1) -> Dict[str, Any]:
        """Load checkpoint state; raises FileNotFoundError when missing."""
        key = self._key(name, version)
        if self._loader is not None:
            raw = self._loader(key)
        else:
            assert self._directory is not None
            path = self._directory / key
            if not path.is_file():
                raise FileNotFoundError(f"no checkpoint: {key}")
            raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return data["state"]

    def exists(self, name: str, version: int = 1) -> bool:
        """True when the checkpoint can be loaded."""
        try:
            self.load(name, version)
            return True
        except (FileNotFoundError, KeyError):
            return False

    def list_versions(self, name: str) -> List[int]:
        """Versions present for *name*, ascending (directory backend only)."""
        if self._directory is None:
            return []
        prefix = f"{name}.v"
        suffix = ".json"
        versions: List[int] = []
        if self._directory.is_dir():
            for path in self._directory.iterdir():
                fname = path.name
                if fname.startswith(prefix) and fname.endswith(suffix):
                    middle = fname[len(prefix):-len(suffix)]
                    if middle.isdigit():
                        versions.append(int(middle))
        return sorted(versions)

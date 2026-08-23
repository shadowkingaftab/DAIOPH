"""Model information REST routes.

Model metadata comes from an injected ``model_registry`` callable (see
``models/registry/``). Without that dependency the routes report the gap
explicitly instead of inventing model entries.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

__all__ = ["ModelsRoute"]

RegistryFn = Callable[[], List[Dict[str, Any]]]


class ModelsRoute:
    """Handlers for ``/models`` endpoints."""

    def __init__(self, registry_fn: Optional[RegistryFn] = None) -> None:
        self._registry_fn = registry_fn

    def list_models(self) -> Dict[str, Any]:
        """List known models from the injected registry callable."""
        if self._registry_fn is None:
            return {
                "status": "unavailable",
                "error": (
                    "no model registry wired; pass a registry_fn returning "
                    "model metadata dicts"
                ),
                "models": [],
            }
        try:
            models = self._registry_fn()
        except Exception as exc:  # noqa: BLE001 - surface registry failure
            return {"status": "error", "error": str(exc), "models": []}
        return {"status": "ok", "count": len(models), "models": models}

    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Return one model's metadata or an explicit not_found."""
        listing = self.list_models()
        if listing["status"] != "ok":
            return listing
        for model in listing["models"]:
            if model.get("model_id") == model_id or model.get("id") == model_id:
                return {"status": "ok", "model": model}
        return {"status": "not_found", "model_id": model_id}

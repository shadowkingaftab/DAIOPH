"""Default configuration values for the DAIOPH system."""

from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "app": {
        "name": "DAIOPH",
        "version": "1.0.0",
        "environment": "development",
    },
    "models": {
        "classifier": {
            "path": "distilbert-base-uncased",
        },
        "qwen": {
            "path": "models/qwen2-0_5b-instruct-q4_k_m.gguf",
            "context_length": 2048,
        },
        "grok": {
            "api_key": "",
            "model": "grok-2-latest",
            "max_tokens": 2048,
        },
    },
    "orchestrator": {
        "max_workers": 4,
        "default_route": "Hybrid",
        "timeout_seconds": 60,
    },
    "memory": {
        "short_term_limit": 100,
        "db_path": "memory/short_term_memory.db",
    },
    "hardware": {
        "max_ram_gb": 8,
        "energy_saving": True,
    },
    "multimodal": {
        "ocr_enabled": True,
        "speech_enabled": True,
    },
    "federated": {
        "enabled": False,
        "server_url": "",
    },
    "security": {
        "encrypt_memory": True,
        "sandbox_commands": True,
    },
    "observability": {
        "log_level": "INFO",
        "metrics_enabled": True,
        "tracing_enabled": False,
    },
}


def get_defaults() -> Dict[str, Any]:
    """Get the default configuration.

    Returns:
        Dict[str, Any]: Deep copy of defaults.
    """
    import copy

    return copy.deepcopy(DEFAULTS)
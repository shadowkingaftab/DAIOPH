"""Gemini cloud inference adapter for DAIOPH evaluation runs."""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
DEFAULT_TIMEOUT = 30
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def is_api_key_set() -> bool:
    """Return whether a Gemini API key is configured."""
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def run_gemini(
    prompt: str,
    model: str | None = None,
    max_tokens: int = 512,
    temperature: float = 0.7,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Generate a text response through the Gemini GenerateContent API."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "⚠️ GEMINI_API_KEY not set."

    selected_model = model or DEFAULT_MODEL
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
    }
    try:
        response = requests.post(
            API_URL_TEMPLATE.format(model=selected_model),
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
        if response.status_code != 200:
            return f"❌ Gemini API Error ({response.status_code}): {response.text}"
        body = response.json()
        candidates = body.get("candidates", [])
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        text = "".join(part.get("text", "") for part in parts).strip()
        return text or "❌ Gemini returned an empty response."
    except requests.RequestException as exc:
        return f"❌ Gemini API Error: {type(exc).__name__}: {exc}"
    except (TypeError, ValueError, KeyError, IndexError) as exc:
        return f"❌ Gemini response parsing error: {type(exc).__name__}: {exc}"

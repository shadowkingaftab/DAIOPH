"""
grok_cloud.py
-------------
Cloud LLM module using the Grok API (xAI) — PRIMARY inference engine.

This is now the PRIMARY model. Qwen (local) is the fallback.

Set API key before running:
  Windows PowerShell:  $env:GROK_API_KEY = "your-key-here"
  Linux/Mac:           export GROK_API_KEY="your-key-here"
  Or place it in your .env file as: GROK_API_KEY=your-key-here
"""

import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Helper to get config from Streamlit Secrets or Environment
def get_config(key, default=None):
    # 1. Try Streamlit Secrets (Cloud)
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except (ImportError, Exception):
        pass
    
    # 2. Try Environment (Local / Docker)
    return os.getenv(key, default)

GROK_API_KEY    = get_config("GROK_API_KEY")
GROK_API_URL    = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL   = "grok-2"   # grok-2 is the most stable standard model
DEFAULT_TIMEOUT = 30              # seconds


def is_api_key_set() -> bool:
    """Returns True if a Grok API key is available."""
    return bool(GROK_API_KEY and GROK_API_KEY.strip())


def run_grok(
    prompt: str,
    model: str = None,
    max_tokens: int = 512,
    temperature: float = 0.7,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """
    Call the Grok API with automatic model failover.
    """
    api_key = os.getenv("GROK_API_KEY", "").strip()

    if not api_key:
        return "⚠️ GROK_API_KEY not set."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json",
    }
    
    # Try multiple models in case one is not enabled for the user's key
    models_to_try = [model] if model else ["grok-3-mini", "grok-3", "grok-2-1212", "grok-2-latest", "grok-beta", "grok-2", "grok-1"]
    last_error = ""

    for m in models_to_try:
        payload = {
            "model":       m,
            "messages":    [{"role": "user", "content": prompt}],
            "max_tokens":  max_tokens,
            "temperature": temperature,
        }

        try:
            response = requests.post(
                GROK_API_URL, headers=headers, json=payload, timeout=timeout
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            
            last_error = f"{response.status_code} - {response.text}"
            if response.status_code in [401, 429]: # Auth/Rate Limit
                break
        except Exception as e:
            last_error = str(e)

    return f"❌ Grok API Error (tried {models_to_try}): {last_error}"


def run_grok_with_fallback(
    prompt: str,
    model: str = None,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> tuple[str, str]:
    """
    Try Grok first. If it fails (no key, timeout, error), fall back to local Qwen.

    Returns:
        (response_text, source) where source is "grok" or "qwen".
    """
    from qwen_oda import run_qwen, is_model_downloaded

    grok_resp = run_grok(prompt, model=model, max_tokens=max_tokens, temperature=temperature)

    # If Grok returned cleanly (no error prefix), use it
    if not grok_resp.startswith(("❌", "⚠️", "Grok API", "No capacity", "timed out", "connection", "Unexpected")):
        return grok_resp, "grok"

    # Grok failed — fall back to local Qwen
    print(f"[router] Grok unavailable: {grok_resp[:80]}", flush=True)

    if not is_model_downloaded():
        return (
            f"Grok is currently unavailable: {grok_resp}\n\n"
            "Local Qwen fallback: model not downloaded yet.\n"
            "Click 'Download Qwen GGUF' in the sidebar to enable offline inference.",
            "none",
        )

    qwen_resp = run_qwen(prompt, max_new_tokens=max_tokens, temperature=temperature)
    return qwen_resp, "qwen"


# ── Self-test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_prompt = "What is edge AI? Answer in one sentence."
    resp, source = run_grok_with_fallback(test_prompt)
    print(f"Source : {source}")
    print(f"Output : {resp.encode('ascii', 'ignore').decode('ascii')}")

# Reuse HTTP sessions in Grok client
import requests
session = requests.Session()
def generate(prompt, **kwargs):
    return session.post(GROK_API_URL, **kwargs)

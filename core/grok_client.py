"""
core/grok_client.py
-------------------
Memory-efficient Grok API client using:
  - Singleton pattern   — only one instance ever created
  - requests.Session()  — reuses TCP connections (faster + less RAM)
  - Model failover      — tries multiple models automatically
  - Graceful errors     — never raises, always returns a string
"""

import requests
import json


class GrokClient:
    """Singleton Grok API client with persistent HTTP session."""

    _instance = None

    def __new__(cls, api_key: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, api_key: str = None):
        # Only initialize once — __init__ is called even on cached __new__
        if self._initialized:
            # Allow updating the API key if a new one is passed
            if api_key and api_key != self.api_key:
                self.api_key = api_key
                self.session.headers.update({"Authorization": f"Bearer {api_key}"})
            return

        self.api_key  = api_key or ""
        self.base_url = "https://api.x.ai/v1/chat/completions"
        self.models   = [
            "grok-2-latest",
            "grok-beta",
            "grok-3-mini",
            "grok-2-1212"
        ]

        # Persistent session reuses TCP connections — saves ~20ms per request
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        })
        self._initialized = True

    def generate(
        self,
        prompt:      str,
        max_tokens:  int   = 512,
        temperature: float = 0.7,
        model:       str   = None,
    ) -> str:
        """
        Call the Grok API with automatic model failover.

        Args:
            prompt      : User prompt.
            max_tokens  : Maximum tokens to generate.
            temperature : Sampling temperature (0 = deterministic).
            model       : Force a specific model (optional).

        Returns:
            Response text, or an error string starting with '⚠️'.
        """
        if not self.api_key or not self.api_key.strip():
            return "⚠️ GROK_API_KEY not set. Add it in the sidebar or .env file."

        models_to_try = [model] if model else self.models
        last_error    = "Unknown error"

        for m in models_to_try:
            payload = {
                "model":       m,
                "messages":    [{"role": "user", "content": prompt}],
                "max_tokens":  max_tokens,
                "temperature": temperature,
                "stream":      False,
            }
            try:
                resp = self.session.post(
                    self.base_url,
                    data=json.dumps(payload),
                    timeout=30,
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]

                last_error = f"HTTP {resp.status_code}: {resp.text[:120]}"

                # Auth / rate-limit errors — no point trying other models
                if resp.status_code in (401, 429):
                    break

            except requests.exceptions.Timeout:
                last_error = f"Timeout on model {m}"
            except requests.exceptions.ConnectionError:
                last_error = "Connection error — check internet"
                break
            except Exception as e:
                last_error = str(e)

        return f"⚠️ Grok API error: {last_error}"

    def update_key(self, new_key: str):
        """Hot-swap the API key without recreating the client."""
        self.api_key = new_key
        self.session.headers.update({"Authorization": f"Bearer {new_key}"})

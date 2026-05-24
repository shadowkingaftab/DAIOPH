import requests
import json

class GrokClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> str:
        """Call Grok API with automatic model failover."""
        # PRIORITIZE MODELS THAT ARE MOST LIKELY TO WORK
        models_to_try = [
            "grok-2-1212",
            "grok-2",
            "grok-beta",
            "grok-1",
            "grok-3-mini",
            "grok-2-latest"
        ]
        last_error = ""

        for model in models_to_try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=20
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                
                last_error = f"{response.status_code} - {response.text}"
                # If it's a 401 (Auth) or 429 (Rate Limit), don't bother retrying other models
                if response.status_code in [401, 429]:
                    break
            except Exception as e:
                last_error = str(e)
        
        return f"Error calling Grok API (tried {', '.join(models_to_try)}): {last_error}"

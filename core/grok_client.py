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
        """Call Grok API for text generation."""
        # Use grok-2 as the most compatible model name
        payload = {
            "model": "grok-2",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            if response.status_code != 200:
                return f"Error calling Grok API: {response.status_code} - {response.text}"
            
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling Grok API: {str(e)}"

from typing import Dict, Optional
from llama_cpp import Llama
from core.grok_client import GrokClient

class TaskExecutor:
    def __init__(self, qwen_path: str, grok_api_key: Optional[str] = None):
        try:
            import gc
            gc.collect()  # Force garbage collection before allocating massive Llama KV cache memory
            self.qwen = Llama(
                model_path=qwen_path,
                n_ctx=512,   # Drastically reduced from 2048 to save KV cache RAM
                n_threads=1, # Reduced to 1 to minimize thread stack memory
                n_batch=128, # Lower batch size to reduce allocation spikes
                n_gpu_layers=0
            )
            self.HAS_QWEN = True
            self.qwen_error = None
        except Exception as e:
            self.HAS_QWEN = False
            self.qwen_error = str(e)
            print(f"Qwen2-0.5B disabled: {str(e)}")

        self.grok = GrokClient(grok_api_key) if grok_api_key else None
        self.HAS_GROK = grok_api_key is not None

    def execute(self, task: Dict, context: Optional[str] = None, pdf_text: Optional[str] = None, route: str = "Hybrid") -> str:
        if context:
            prompt = f"Context:\n{context}\n\nTask: {task['task']}"
        elif pdf_text:
            prompt = f"PDF Content:\n{pdf_text[:2000]}...\n\nTask: {task['task']}"
        else:
            prompt = task["task"]

        try:
            if route == "ODA" and self.HAS_QWEN:
                return self.qwen(prompt=prompt, max_tokens=512, temperature=0.7)["choices"][0]["text"].strip()
            elif route == "Cloud" and self.HAS_GROK:
                return self.grok.generate(prompt, max_tokens=512, temperature=0.7)
            elif self.HAS_QWEN:  # Hybrid: Try Qwen first
                return self.qwen(prompt=prompt, max_tokens=512, temperature=0.7)["choices"][0]["text"].strip()
            elif self.HAS_GROK:
                return self.grok.generate(prompt, max_tokens=512, temperature=0.7)
            else:
                return "Error: No models available for execution."
        except Exception as e:
            if route != "ODA" and self.HAS_GROK:
                return self.grok.generate(prompt, max_tokens=512, temperature=0.7)
            else:
                return f"Error: {str(e)}"

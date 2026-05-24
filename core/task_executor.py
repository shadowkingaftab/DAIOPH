from typing import Dict, Optional
from core.grok_client import GrokClient
import threading

class TaskExecutor:
    def __init__(self, qwen_path: str, grok_api_key: Optional[str] = None):
        self.lock = threading.Lock()
        # Lazy-import llama_cpp so the app doesn't crash on Streamlit Cloud
        try:
            from llama_cpp import Llama
            import gc
            gc.collect()
            self.qwen = Llama(
                model_path=qwen_path,
                n_ctx=512,
                n_threads=1,
                n_batch=128,
                n_gpu_layers=0
            )
            self.HAS_QWEN = True
            self.qwen_error = None
        except ImportError:
            self.HAS_QWEN = False
            self.qwen_error = "llama-cpp-python not installed (Streamlit Cloud — Grok API will be used instead)"
            print(f"Qwen2-0.5B disabled: {self.qwen_error}")
        except Exception as e:
            import traceback
            self.HAS_QWEN = False
            self.qwen_error = f"{type(e).__name__}: {str(e)}"
            print(f"Qwen2-0.5B disabled: {self.qwen_error}")

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
                with self.lock:
                    return self.qwen.create_chat_completion(messages=[{"role": "user", "content": prompt}], max_tokens=512, temperature=0.7)["choices"][0]["message"]["content"].strip()
            elif route == "Cloud":
                if self.HAS_GROK:
                    res = self.grok.generate(prompt, max_tokens=512, temperature=0.7)
                    if not res.startswith("Error calling Grok API"):
                        return res
                    print(f"Grok failed, falling back to Qwen: {res}")
                
                if self.HAS_QWEN:
                    with self.lock:
                        return self.qwen.create_chat_completion(
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=512,
                            temperature=0.7
                        )["choices"][0]["message"]["content"].strip()
                return "Error: No models available (Grok failed and Qwen not loaded)"
            elif self.HAS_GROK:
                return self.grok.generate(prompt, max_tokens=512, temperature=0.7)
            else:
                return "❌ No models available. Please add your Grok API key in the sidebar."
        except Exception as e:
            if route != "ODA" and self.HAS_GROK:
                return self.grok.generate(prompt, max_tokens=512, temperature=0.7)
            else:
                return f"Error: {str(e)}"

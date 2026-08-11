"""
task_executor.py
----------------
Executes individual DAG tasks using the selected inference route.

Features:
  - Never-give-up execution with exponential backoff retry (up to 3 attempts)
  - Automatic route fallback: ODA → Hybrid → Cloud
  - Thread-safe Qwen inference via threading.Lock
  - Retry counter tracking for transparency
"""

import time
import math
import threading
from typing import Dict, Optional
from core.grok_client import GrokClient


class TaskExecutor:
    def __init__(self, qwen_path: str, grok_api_key: Optional[str] = None):
        self.lock = threading.Lock()

        # ── Lazy-import llama_cpp so the app doesn't crash on Streamlit Cloud ──
        try:
            from llama_cpp import Llama
            import gc
            gc.collect()
            self.qwen = Llama(
                model_path=qwen_path,
                n_ctx=512,
                n_threads=2,           # Reduced for Streamlit Cloud compatibility
                n_batch=128,
                n_gpu_layers=0,
                verbose=False,
            )
            self.HAS_QWEN = True
            self.qwen_error = None
        except ImportError:
            self.HAS_QWEN = False
            self.qwen_error = "llama-cpp-python not installed (Streamlit Cloud — Grok API will be used instead)"
            print(f"Qwen2-0.5B disabled: {self.qwen_error}")
        except Exception as e:
            self.HAS_QWEN = False
            self.qwen_error = f"{type(e).__name__}: {str(e)}"
            print(f"Qwen2-0.5B disabled: {self.qwen_error}")

        self.grok = GrokClient(grok_api_key) if grok_api_key else None
        self.HAS_GROK = grok_api_key is not None

        # Track retry counts per task
        self.retry_counts: Dict[str, int] = {}

    def _run_qwen(self, prompt: str) -> str:
        """Thread-safe Qwen inference."""
        with self.lock:
            completion = self.qwen.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.7,
            )
            return completion["choices"][0]["message"]["content"].strip()

    def _run_grok(self, prompt: str) -> str:
        """Grok cloud inference."""
        res = self.grok.generate(prompt, max_tokens=512, temperature=0.7)
        if res and not res.startswith(("Error calling Grok API", "Error:")):
            return res
        raise RuntimeError(f"Grok returned error: {res}")

    def execute(
        self,
        task: Dict,
        context: Optional[str] = None,
        pdf_text: Optional[str] = None,
        route: str = "Hybrid",
    ) -> str:
        """
        Execute a single task with never-give-up logic.

        Retry strategy:
          - Attempt 0: Immediate try
          - Attempt 1: 1s backoff (2^0)
          - Attempt 2: 2s backoff (2^1)
          - Attempt 3: 4s backoff (2^2)
          - After max retries: fallback route (ODA→Cloud, Hybrid→Cloud)
        """
        # Build the full prompt with context
        if context:
            prompt = f"Context:\n{context}\n\nTask: {task['task']}"
        elif pdf_text:
            prompt = f"PDF Content:\n{pdf_text[:2000]}...\n\nTask: {task['task']}"
        else:
            prompt = task["task"]

        task_id = task.get("id", "unknown")
        self.retry_counts[task_id] = 0

        return self._execute_with_retry(task_id, prompt, route, attempt=0)

    def _execute_with_retry(self, task_id: str, prompt: str, route: str, attempt: int = 0) -> str:
        """
        Internal retry loop with exponential backoff.
        Falls back to Cloud route after max retries on ODA/Hybrid.
        """
        MAX_RETRIES = 3

        try:
            if route == "ODA":
                if self.HAS_QWEN:
                    return self._run_qwen(prompt)
                elif self.HAS_GROK:
                    print(f"[executor] ODA→Cloud fallback for {task_id}")
                    return self._run_grok(prompt)
                else:
                    return "❌ No models available. Please add your Grok API key in the sidebar."

            elif route == "Cloud":
                if self.HAS_GROK:
                    return self._run_grok(prompt)
                elif self.HAS_QWEN:
                    print(f"[executor] Cloud→ODA fallback for {task_id}")
                    return self._run_qwen(prompt)
                else:
                    return "❌ No models available. Please add your Grok API key in the sidebar."

            else:  # Hybrid
                if self.HAS_QWEN:
                    return self._run_qwen(prompt)
                elif self.HAS_GROK:
                    return self._run_grok(prompt)
                else:
                    return "❌ No models available. Please add your Grok API key in the sidebar."

        except Exception as e:
            self.retry_counts[task_id] = self.retry_counts.get(task_id, 0) + 1

            if attempt < MAX_RETRIES:
                backoff = math.pow(2, attempt)  # 1s, 2s, 4s
                print(f"[executor] Task {task_id} failed (attempt {attempt+1}/{MAX_RETRIES}), "
                      f"retrying in {backoff:.0f}s... Error: {e}")
                time.sleep(backoff)
                return self._execute_with_retry(task_id, prompt, route, attempt + 1)

            # Max retries exceeded — try another route
            if route in ("ODA", "Hybrid") and self.HAS_GROK:
                print(f"[executor] Task {task_id} max retries exceeded, falling back to Cloud.")
                return self._execute_with_retry(task_id, prompt, "Cloud", 0)

            return f"Error after {MAX_RETRIES} retries: {str(e)}"

    def get_retry_counts(self) -> Dict[str, int]:
        """Return the retry count per task_id for display in UI."""
        return {k: v for k, v in self.retry_counts.items() if v > 0}

    def reset_retry_counts(self):
        """Reset retry tracking between executions."""
        self.retry_counts = {}

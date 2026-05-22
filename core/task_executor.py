from typing import Dict, Optional
from llama_cpp import Llama
from core.grok_client import GrokClient
import os
from huggingface_hub import hf_hub_download


def _resolve_model_path(qwen_path: str) -> str:
    """Resolve model path — use local file if it exists, else download from HF."""
    # Check if the file exists at the given path
    if os.path.isfile(qwen_path):
        return qwen_path
    # Check in project root
    root_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), qwen_path)
    if os.path.isfile(root_path):
        return root_path
    # Fallback: download from HuggingFace
    return hf_hub_download(
        repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
        filename="qwen2-0_5b-instruct-q4_k_m.gguf"
    )


class TaskExecutor:
    """Executes individual tasks using Qwen2-0.5B (local) or Grok (cloud)."""

    def __init__(self, qwen_path: str, grok_api_key: Optional[str] = None):
        resolved_path = _resolve_model_path(qwen_path)
        self.qwen = Llama(
            model_path=resolved_path,
            n_ctx=4096,
            n_threads=8,
            n_gpu_layers=0
        )
        self.grok = GrokClient(grok_api_key) if grok_api_key else None

    def execute(
        self,
        task: Dict,
        context: Optional[str] = None,
        pdf_text: Optional[str] = None,
        route: str = "Hybrid"
    ) -> str:
        """Execute a task with Qwen2-0.5B or Grok (based on route)."""
        # Build the prompt
        if context:
            prompt = f"Context:\n{context}\n\nTask: {task['task']}"
        elif pdf_text:
            prompt = f"PDF Content:\n{pdf_text[:2000]}...\n\nTask: {task['task']}"
        else:
            prompt = task["task"]

        try:
            if route == "ODA" or not self.grok:
                # ODA: Use Qwen2-0.5B only
                output = self.qwen(
                    prompt=prompt, max_tokens=512, temperature=0.7
                )["choices"][0]["text"].strip()
            elif route == "Cloud":
                # Cloud: Use Grok first, fall back to Qwen
                output = self.grok.generate(prompt, max_tokens=512, temperature=0.7)
            else:  # Hybrid
                # Hybrid: Try Qwen first, fall back to Grok
                output = self.qwen(
                    prompt=prompt, max_tokens=512, temperature=0.7
                )["choices"][0]["text"].strip()
        except Exception as e:
            if route != "ODA" and self.grok:
                output = self.grok.generate(prompt, max_tokens=512, temperature=0.7)
            else:
                output = f"Error executing task: {str(e)}"
        return output

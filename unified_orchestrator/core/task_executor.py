from typing import Dict
from llama_cpp import Llama
import os

class TaskExecutor:
    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
            
        self.qwen = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=8,
            n_gpu_layers=0,
            verbose=False
        )

    def execute(self, task: Dict, context: str = None, pdf_text: str = None) -> str:
        """Execute task with Qwen (on-device)."""
        if context:
            prompt = f"Context:\n{context}\n\nTask: {task['task']}"
        elif pdf_text:
            prompt = f"PDF Content:\n{pdf_text[:2000]}...\n\nTask: {task['task']}"
        else:
            prompt = task["task"]
            
        # Wrap in ChatML format for Qwen
        formatted_prompt = (
            "<|im_start|>system\nYou are a helpful assistant. Complete the task based on context.<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        )

        # Check if the task requires internet or is complex
        text_lower = task["task"].lower()
        requires_internet = any(kw in text_lower for kw in ["search", "latest", "news", "weather", "current", "research", "grok", "cloud"])
        
        if requires_internet or task.get("model") == "grok":
            import sys
            import os
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
            try:
                from grok_cloud import run_grok_with_fallback
                # Use Grok for execution
                output, _ = run_grok_with_fallback(prompt, max_tokens=512, temperature=0.7)
                return output.strip()
            except ImportError:
                pass
                
        # Default: Fast On-Device Qwen Execution
        output = self.qwen(
            prompt=formatted_prompt,
            max_tokens=512,
            temperature=0.7,
            stop=["<|im_end|>", "<|im_start|>"]
        )["choices"][0]["text"].strip()
        
        return output

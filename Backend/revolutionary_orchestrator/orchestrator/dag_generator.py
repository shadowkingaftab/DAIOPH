from typing import Dict
from llama_cpp import Llama
import json
import re
import torch


class DAGGenerator:
    """
    Uses the local Qwen GGUF model (via llama-cpp-python) to dynamically
    generate a Directed Acyclic Graph (DAG) of micro-tasks from any prompt.
    No hardcoding. No external API calls.
    """

    def __init__(self, model_path: str):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=8,
            n_gpu_layers=0,
            verbose=False
        )

    def generate(self, prompt: str) -> Dict:
        """Generate a DAG of micro-prompts from the input prompt."""
        system_msg = (
            "You are an expert task compiler. Convert the user's complex prompt "
            "into a Directed Acyclic Graph (DAG) of executable micro-tasks. "
            "Respond ONLY with valid JSON — no explanation, no markdown fences."
        )

        example = json.dumps({
            "dag": {
                "nodes": [
                    {"id": "n1", "task": "Extract key points from the document", "model": "qwen", "output_type": "list"},
                    {"id": "n2", "task": "Summarize the extracted points", "model": "qwen", "output_type": "text", "depends_on": ["n1"]},
                    {"id": "n3", "task": "Draft a professional response email", "model": "qwen", "output_type": "text", "depends_on": ["n2"]}
                ]
            },
            "metadata": {"complexity": 3, "estimated_tokens": 600}
        }, indent=2)

        full_prompt = (
            f"<|im_start|>system\n{system_msg}<|im_end|>\n"
            f"<|im_start|>user\n"
            f"Example output format:\n{example}\n\n"
            f"Now compile this prompt into a DAG:\n{prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        response = self.llm(
            full_prompt,
            max_tokens=600,
            temperature=0.3,
            stop=["<|im_end|>"]
        )
        text = response["choices"][0]["text"].strip()

        # Extract JSON from the response
        try:
            # Try to find a JSON block
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

        # Fallback: single-node DAG
        return {
            "dag": {
                "nodes": [{
                    "id": "n1",
                    "task": prompt,
                    "model": "qwen",
                    "output_type": "text"
                }]
            },
            "metadata": {"complexity": 1, "estimated_tokens": 256}
        }

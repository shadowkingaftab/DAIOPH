"""
planner.py — DAG planning brain (structured JSON, low-temperature, PDF-aware)
"""
from typing import Dict, Optional
from llama_cpp import Llama
import json


class TaskPlanner:
    def __init__(self, model_path: str, shared_llm=None):
        if shared_llm:
            self.llm = shared_llm
        else:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_threads=8,
                n_gpu_layers=0,
                verbose=False,
                seed=42
            )

    def plan(self, prompt: str, pdf_text: Optional[str] = None) -> Dict:
        """
        Generate a DAG of micro-tasks.
        If pdf_text is provided, a 600-char excerpt is injected so the planner
        can write document-aware task descriptions.
        """
        # Check for sequential keywords (e.g., "First... Then...") to force splitting without LLM
        import re
        sequential_match = re.search(
            r'^(.*?)\b(First|Initially|Start by|Step 1:?|Do)\b\s*(.*?)\s*\b(Then|Next|After that|Step 2:?|do)\b\s*(.*?)(?:\s*\b(Finally|Lastly|Step 3:?)\b\s*(.*))?$',
            prompt,
            re.IGNORECASE | re.DOTALL
        )

        if sequential_match:
            prefix = sequential_match.group(1).strip()
            task1_core = sequential_match.group(3).strip().lstrip(':,.- ').strip()
            task2_core = sequential_match.group(5).strip().lstrip(':,.- ').strip()
            task3_core = sequential_match.group(7)
            
            task1 = f"{prefix} {task1_core}".strip() if prefix else task1_core
            task2 = task2_core
            
            nodes = [
                {"id": "n1", "task": task1, "model": "qwen"},
                {"id": "n2", "task": task2, "model": "qwen", "depends_on": ["n1"]}
            ]
            
            if task3_core:
                task3 = task3_core.strip().lstrip(':,.- ').strip()
                nodes.append({"id": "n3", "task": task3, "model": "qwen", "depends_on": ["n2"]})
                
            return {"nodes": nodes}
            
        # Select context-appropriate example to avoid confusing small local models
        if pdf_text and pdf_text.strip():
            example = json.dumps({
                "nodes": [
                    {"id": "n1", "task": "Extract key points from the document", "model": "qwen"},
                    {"id": "n2", "task": "Write a structured summary", "model": "qwen", "depends_on": ["n1"]},
                    {"id": "n3", "task": "Generate a conclusion paragraph", "model": "qwen", "depends_on": ["n2"]}
                ]
            })
        else:
            example = json.dumps({
                "nodes": [
                    {"id": "n1", "task": "Outline the key topics for a professional blog post", "model": "qwen"},
                    {"id": "n2", "task": "Draft the introductory paragraph", "model": "qwen", "depends_on": ["n1"]},
                    {"id": "n3", "task": "Write the main content sections based on the outline", "model": "qwen", "depends_on": ["n2"]}
                ]
            })

        doc_context = ""
        if pdf_text and pdf_text.strip():
            preview = pdf_text.strip()[:600]
            doc_context = f'\nDocument excerpt:\n"""\n{preview}\n"""\n'

        planning_prompt = (
            "<|im_start|>system\n"
            "You are a task planning expert. Convert the user prompt into a list of atomic tasks "
            "as JSON. Output ONLY valid JSON — no markdown, no explanation.\n"
            "CRITICAL: Do NOT copy the task descriptions from the example. Decompose the actual User Prompt into specific steps.\n"
            "<|im_end|>\n"
            "<|im_start|>user\n"
            f"Format Example:\n{example}\n\n"
            f"Rules:\n"
            f"- Tasks with no dependencies: omit 'depends_on' key entirely\n"
            f"- Tasks needing prior results: list them in 'depends_on'\n"
            f"- Always set model to 'qwen'\n"
            f"- If a document is provided, reference it in task descriptions\n"
            f"{doc_context}\n"
            f"User Prompt: {prompt}\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

        response = self.llm(
            planning_prompt,
            max_tokens=400,
            temperature=0.1,
            top_p=0.9,
            repeat_penalty=1.0,
            stop=["<|im_end|>", "<|im_start|>"]
        )

        text = response["choices"][0]["text"].strip()

        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                parsed = json.loads(text[start:end])
                
                # Check for "nodes" or "dag"
                nodes = None
                if "nodes" in parsed:
                    nodes = parsed["nodes"]
                elif "dag" in parsed and "nodes" in parsed["dag"]:
                    nodes = parsed["dag"]["nodes"]

                if nodes:
                    # Guardrail: Check if the tiny local model copied the example verbatim
                    is_copycat = False
                    forbidden_keywords = [
                        "extract key points from the document",
                        "write a structured summary",
                        "generate a conclusion paragraph",
                        "outline the key topics",
                        "draft the introductory paragraph",
                        "write the main content sections"
                    ]
                    for node in nodes:
                        task_lower = node.get("task", "").lower()
                        if any(kw in task_lower for kw in forbidden_keywords):
                            is_copycat = True
                            break

                    if not is_copycat:
                        return {"nodes": nodes}
        except (json.JSONDecodeError, KeyError):
            pass

        # Fallback: treat the whole prompt as one task to guarantee 100% correct, custom execution
        return {"nodes": [{"id": "n1", "task": prompt, "model": "qwen"}]}

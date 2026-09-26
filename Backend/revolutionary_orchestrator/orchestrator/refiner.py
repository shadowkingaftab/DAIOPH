"""
refiner.py
----------
Self-refines a DAG based on execution feedback.

Uses the SAME model as the planner (small, deterministic, structured output)
to analyze what went wrong and produce an improved DAG.
"""
from typing import Dict
from llama_cpp import Llama
import json


class TaskRefiner:
    """
    DAG optimizer — reviews execution results and rewrites the DAG if needed.
    Shares the same model config as the planner: small context, low temperature.
    """

    def __init__(self, model_path: str, shared_llm=None):
        if shared_llm:
            self.llm = shared_llm
        else:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=1024,
                n_threads=8,
                n_gpu_layers=0,
                verbose=False,
                seed=42
            )

    def refine(self, dag: Dict, execution_results: Dict) -> Dict:
        """
        Analyze execution results and return an improved DAG if needed.

        Args:
            dag:               The original DAG ({"nodes": [...]}).
            execution_results: Mapping of node_id → output or {"error": ...}.

        Returns:
            Improved DAG dict, or the original if no improvement is needed.
        """
        # ── Collect feedback on failed/poor tasks ──────────────────────────────
        feedback_lines = []
        for node in dag.get("nodes", []):
            task_id = node["id"]
            result = execution_results.get(task_id)
            if result is None:
                feedback_lines.append(f"- Task {task_id} did not execute.")
            elif isinstance(result, dict) and "error" in result:
                feedback_lines.append(f"- Task {task_id} failed: {result['error']}")
            elif isinstance(result, str) and len(result.split()) < 15:
                feedback_lines.append(
                    f"- Task {task_id} output too short ({len(result.split())} words): '{result[:80]}'"
                )

        if not feedback_lines:
            return dag  # Nothing to fix

        feedback_text = "\n".join(feedback_lines)
        original_dag_str = json.dumps(dag, indent=2)

        refinement_prompt = (
            "<|im_start|>system\n"
            "You are a task graph optimizer. Your ONLY job is to fix a broken task DAG. "
            "Output ONLY valid JSON with the improved nodes list. No explanation, no markdown.\n"
            "<|im_end|>\n"
            "<|im_start|>user\n"
            f"Problems found:\n{feedback_text}\n\n"
            f"Original DAG:\n{original_dag_str}\n\n"
            f"Rules for improvement:\n"
            f"1. Split failed tasks into smaller, simpler sub-tasks\n"
            f"2. Add intermediate steps where output was too short\n"
            f"3. Keep the same JSON format: {{\"nodes\": [...]}}\n"
            f"4. Preserve working tasks unchanged\n"
            f"5. Use sequential IDs (n1, n2, n3...)\n\n"
            f"Improved DAG:\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

        response = self.llm(
            refinement_prompt,
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
                if "nodes" in parsed:
                    return parsed
                if "dag" in parsed and "nodes" in parsed["dag"]:
                    return parsed["dag"]
        except (json.JSONDecodeError, KeyError):
            pass

        return dag  # Return original if parsing fails

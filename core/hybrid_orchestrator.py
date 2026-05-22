from typing import Dict, Tuple, Optional
from core.task_executor import TaskExecutor
from core.grok_client import GrokClient
import re


class HybridOrchestrator:
    """
    Orchestrator that decomposes prompts into a DAG of micro-tasks,
    then executes them via Qwen (local) and/or Grok (cloud).
    """

    def __init__(
        self,
        distilbert_path: str,
        qwen_path: str,
        grok_api_key: Optional[str] = None
    ):
        self.executor = TaskExecutor(qwen_path, grok_api_key)
        self.grok_api_key = grok_api_key
        self.grok = GrokClient(grok_api_key) if grok_api_key else None

    def execute(
        self,
        prompt: str,
        pdf_text: Optional[str] = None,
        route: str = "Hybrid"
    ) -> Tuple[Dict, Dict]:
        """Execute prompt: plan → execute → refine if needed."""
        dag = self._plan(prompt, pdf_text)
        results = self._execute(dag, pdf_text, route)

        # Retry failed tasks once
        if any(isinstance(r, dict) and "error" in r for r in results.values()):
            dag = self._refine(dag, results)
            results = self._execute(dag, pdf_text, route)

        return dag, results

    def _plan(self, prompt: str, pdf_text: Optional[str] = None) -> Dict:
        """
        Generate a DAG of micro-tasks from the user prompt.
        Uses rule-based splitting (DistilBERT integration point).
        """
        # Pattern 1: Sequential prompts ("First X, then Y")
        sequential_match = re.search(
            r'(First|Initially|Start by|Step\s*\d+[:\.])\s*(.*?)\s*'
            r'(Then|Next|After that|Finally|Step\s*\d+[:\.])\s*(.*)',
            prompt,
            re.IGNORECASE | re.DOTALL
        )
        if sequential_match:
            return {
                "dag": {
                    "nodes": [
                        {
                            "id": "n1",
                            "task": sequential_match.group(2).strip().rstrip(".,;"),
                            "model": "qwen"
                        },
                        {
                            "id": "n2",
                            "task": sequential_match.group(4).strip().rstrip(".,;"),
                            "model": "qwen",
                            "depends_on": ["n1"]
                        }
                    ]
                }
            }

        # Pattern 2: Long prompts → split into summarize + expand
        if len(prompt.split()) > 20:
            return {
                "dag": {
                    "nodes": [
                        {
                            "id": "n1",
                            "task": f"Summarize the main points of: {prompt}",
                            "model": "qwen"
                        },
                        {
                            "id": "n2",
                            "task": "Expand on the summary with detailed steps or analysis.",
                            "model": "qwen",
                            "depends_on": ["n1"]
                        }
                    ]
                }
            }

        # Default: Single task
        return {
            "dag": {
                "nodes": [
                    {"id": "n1", "task": prompt, "model": "qwen"}
                ]
            }
        }

    def _execute(
        self,
        dag: Dict,
        pdf_text: Optional[str] = None,
        route: str = "Hybrid"
    ) -> Dict:
        """Execute each node in topological order, passing context from dependencies."""
        results = {}
        for node in dag["dag"]["nodes"]:
            # Build context from completed dependencies
            context = None
            if "depends_on" in node:
                dep_outputs = [
                    str(results[dep]) for dep in node["depends_on"]
                    if dep in results and not (isinstance(results[dep], dict) and "error" in results[dep])
                ]
                if dep_outputs:
                    context = "\n\n".join(dep_outputs)

            results[node["id"]] = self.executor.execute(node, context, pdf_text, route)
        return results

    def _refine(self, dag: Dict, results: Dict) -> Dict:
        """Refine DAG if tasks failed (simple retry for now)."""
        return dag

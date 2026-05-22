from typing import Dict, Tuple
from core.task_planner import TaskPlanner
from core.task_executor import TaskExecutor
from core.task_refiner import TaskRefiner
from core.stream_handler import StreamHandler
from concurrent.futures import ThreadPoolExecutor, as_completed

class HybridOrchestrator:
    def __init__(self, bartllm_path: str, qwen_path: str):
        self.planner = TaskPlanner(bartllm_path)
        self.executor = TaskExecutor(qwen_path)
        self.refiner = TaskRefiner(bartllm_path)
        self.stream_handler = StreamHandler()

    def execute(self, prompt: str, pdf_text: str = None) -> Tuple[Dict, Dict]:
        """Execute prompt with hybrid (Edge AI + Bifurcation) approach."""
        # Step 1: Plan (Grok - Cloud)
        with self.stream_handler.stream("Planning tasks with Cloud LLM (Grok)..."):
            dag = self.planner.plan(prompt, pdf_text)

        # Step 2: Execute (Qwen - On-Device)
        results = {}
        # Since llama_cpp is not thread-safe and we need sequential processing,
        # we process sequentially ensuring context dependencies are met
        nodes = dag.get("dag", {}).get("nodes", [])
        if not nodes:
            # Fallback for old format
            nodes = dag.get("nodes", [])
            if nodes:
                if "dag" not in dag:
                    dag["dag"] = {}
                dag["dag"]["nodes"] = nodes
                
        for node in nodes:
            self.stream_handler.stream(f"Executing task {node['id']} with Qwen...")
            try:
                if "depends_on" in node and node["depends_on"]:
                    context = "\n\n".join(str(results.get(dep, "")) for dep in node["depends_on"])
                    result = self.executor.execute(node, context, pdf_text)
                else:
                    result = self.executor.execute(node, None, pdf_text)
                results[node["id"]] = result
                self.stream_handler.stream(f"✅ Task {node['id']} completed.")
            except Exception as e:
                results[node["id"]] = {"error": str(e)}
                self.stream_handler.stream(f"❌ Task {node['id']} failed: {str(e)}")

        # Step 3: Refine if needed
        if any(isinstance(r, dict) and "error" in r for r in results.values()):
            with self.stream_handler.stream("Refining tasks with Cloud LLM..."):
                dag = self.refiner.refine(dag, results)
                # Retry execution
                results = {}
                nodes = dag.get("dag", {}).get("nodes", [])
                for node in nodes:
                    try:
                        results[node["id"]] = self.executor.execute(node, None, pdf_text)
                        self.stream_handler.stream(f"✅ Retried task {node['id']}.")
                    except Exception as e:
                        results[node["id"]] = {"error": str(e)}

        return dag, results

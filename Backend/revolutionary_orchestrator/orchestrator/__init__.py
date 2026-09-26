from typing import Dict, Optional
from .planner import TaskPlanner
from .executor import TaskExecutor
from .refiner import TaskRefiner
from .visualizer import visualize_dag
from llama_cpp import Llama

class LLMOrchestrator:
    """
    Full LLMCompiler + Self-Refine pipeline.
    Shares a single Llama instance if the model paths are identical to avoid ggml crashes.
    """

    def __init__(self, planner_model_path: str, executor_model_path: str):
        self.planner_model_path = planner_model_path
        self.executor_model_path = executor_model_path
        
        if planner_model_path == executor_model_path:
            # Create a single shared instance with the larger context size to prevent ggml crashes
            self.shared_llm = Llama(
                model_path=planner_model_path,
                n_ctx=4096,
                n_threads=8,
                n_gpu_layers=0,
                verbose=False
            )
            self.planner = TaskPlanner(planner_model_path, shared_llm=self.shared_llm)
            self.executor = TaskExecutor(executor_model_path, shared_llm=self.shared_llm)
            self.refiner = TaskRefiner(planner_model_path, shared_llm=self.shared_llm)
        else:
            self.planner = TaskPlanner(planner_model_path)
            self.executor = TaskExecutor(executor_model_path)
            self.refiner = TaskRefiner(planner_model_path)

    def execute(self, prompt: str, pdf_text: Optional[str] = None) -> Dict:
        """Full pipeline: Plan → Execute → (Refine if needed) → Return results."""
        dag = self.planner.plan(prompt, pdf_text)

        if not dag or "nodes" not in dag:
            dag = {"nodes": [{"id": "n1", "task": prompt, "model": "qwen"}]}

        results = self.executor.execute(dag, pdf_text)

        has_errors = any(isinstance(r, dict) and "error" in r for r in results.values())
        if has_errors:
            refined_dag = self.refiner.refine(dag, results)
            if refined_dag and "nodes" in refined_dag and refined_dag["nodes"]:
                dag = refined_dag
                results = self.executor.execute(dag, pdf_text)

        all_success = all(not (isinstance(r, dict) and "error" in r) for r in results.values())

        return {
            "dag": dag,
            "execution_results": results,
            "status": "completed" if all_success else "partial"
        }

    def run(self, prompt: str, pdf_text: Optional[str] = None) -> Dict:
        return self.execute(prompt, pdf_text)

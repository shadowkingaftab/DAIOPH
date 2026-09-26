from typing import Dict
import json
import sys
import os

# Ensure root directory is in path to import grok_cloud
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from grok_cloud import run_grok

class TaskRefiner:
    def __init__(self, model_path: str = None):
        pass

    def refine(self, dag: Dict, execution_results: Dict) -> Dict:
        """Analyze execution results and return an improved DAG if needed using Grok."""
        feedback_lines = []
        for node in dag.get("dag", {}).get("nodes", []):
            task_id = node["id"]
            result = execution_results.get(task_id)
            if result is None:
                feedback_lines.append(f"- Task {task_id} did not execute.")
            elif isinstance(result, dict) and "error" in result:
                feedback_lines.append(f"- Task {task_id} failed: {result['error']}")

        if not feedback_lines:
            return dag

        feedback_text = "\n".join(feedback_lines)
        original_dag_str = json.dumps(dag, indent=2)

        refinement_prompt = f"""
        You are a task graph optimizer. Fix a broken task DAG.
        Output ONLY valid JSON with the improved nodes list.
        
        Problems found:
        {feedback_text}
        
        Original DAG:
        {original_dag_str}
        
        Rules:
        1. Split failed tasks into smaller, simpler sub-tasks
        2. Keep the same JSON format: {{"dag": {{"nodes": [...]}}}}
        3. Preserve working tasks unchanged
        
        Improved DAG:
        """

        response = run_grok(refinement_prompt, temperature=0.1)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except Exception:
            pass

        return dag

"""
executor.py — Task execution brain (generative, PDF-aware, sequential)
"""
from typing import Dict, Optional
from llama_cpp import Llama


class TaskExecutor:
    def __init__(self, model_path: str, shared_llm=None):
        if shared_llm:
            self.llm = shared_llm
        else:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=4096,
                n_threads=8,
                n_gpu_layers=0,
                verbose=False
            )

    def execute_single(self, task_text: str, context: str = "") -> str:
        """Run one atomic task, prepending any context (document + parent outputs)."""
        if context:
            prompt = (
                "<|im_start|>system\n"
                "You are a helpful assistant. Use the provided context to complete the task accurately.<|im_end|>\n"
                "<|im_start|>user\n"
                f"[Context]\n{context}\n\n"
                f"[Task]\n{task_text}<|im_end|>\n"
                "<|im_start|>assistant\n"
            )
        else:
            prompt = (
                "<|im_start|>system\n"
                "You are a helpful assistant. Complete the task accurately and thoroughly.<|im_end|>\n"
                "<|im_start|>user\n"
                f"{task_text}<|im_end|>\n"
                "<|im_start|>assistant\n"
            )

        response = self.llm(
            prompt,
            max_tokens=512,
            temperature=0.3,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["<|im_end|>", "<|im_start|>"]
        )
        return response["choices"][0]["text"].strip()

    def execute(self, dag: Dict, pdf_text: Optional[str] = None) -> Dict:
        """
        Execute all DAG tasks in topological order (sequential — llama-cpp is not thread-safe).

        pdf_text is ALWAYS injected as a context preamble for every task, not just
        tasks that happen to mention the word 'PDF'. This ensures the model actually
        reads the document for every step.
        """
        nodes = dag.get("nodes", [])
        if not nodes:
            return {}

        # Sanitize forward/cyclic dependencies from small LLMs
        # Rule: task at index i can only depend on tasks at index < i
        id_to_index = {node["id"]: idx for idx, node in enumerate(nodes)}
        for idx, node in enumerate(nodes):
            raw_deps = node.get("depends_on", [])
            node["depends_on"] = [
                dep for dep in raw_deps
                if dep in id_to_index and id_to_index[dep] < idx
            ]

        # Prepare document preamble (truncated to leave room for task + parent context)
        doc_preamble = ""
        if pdf_text and pdf_text.strip():
            doc_preamble = f"[Document Content]\n{pdf_text.strip()[:2000]}"

        results: Dict[str, object] = {}
        executed: set = set()

        while len(executed) < len(nodes):
            # Collect tasks whose dependencies are all done
            ready = [
                node for node in nodes
                if node["id"] not in executed
                and all(dep in executed for dep in node.get("depends_on", []))
            ]

            if not ready:
                # Break any remaining deadlocks
                for node in nodes:
                    if node["id"] not in executed:
                        node["depends_on"] = []
                continue

            for node in ready:
                task_text = node["task"]

                # Build context: document first, then parent outputs
                context_parts = []
                if doc_preamble:
                    context_parts.append(doc_preamble)

                for dep_id in node.get("depends_on", []):
                    dep_result = results.get(dep_id, "")
                    dep_node = next((n for n in nodes if n["id"] == dep_id), None)
                    dep_label = dep_node["task"][:50] if dep_node else dep_id
                    if dep_result and not isinstance(dep_result, dict):
                        context_parts.append(f"[Step {dep_id} — {dep_label}]\n{dep_result}")

                context = "\n\n".join(context_parts)

                try:
                    results[node["id"]] = self.execute_single(task_text, context)
                except Exception as e:
                    results[node["id"]] = {"error": str(e)}

                executed.add(node["id"])

        return results

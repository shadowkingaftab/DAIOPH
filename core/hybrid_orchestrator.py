from typing import Dict, Tuple, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.grok_client import GrokClient
from core.task_executor import TaskExecutor
import re
import json
import nltk
import copy
from nltk.tokenize import sent_tokenize
from functools import lru_cache
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

class HybridOrchestrator:
    def __init__(self, distilbert_path: str, qwen_path: str, grok_api_key: Optional[str] = None):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(distilbert_path)
            self.distilbert_model = AutoModelForSequenceClassification.from_pretrained(distilbert_path)
            self.distilbert_classifier = pipeline(
                "text-classification",
                model=self.distilbert_model,
                tokenizer=self.tokenizer
            )
            self.HAS_DISTILBERT = True
        except Exception as e:
            import streamlit as st
            st.warning(f"⚠️ DistilBERT disabled: {str(e)}")
            self.HAS_DISTILBERT = False

        self.executor = TaskExecutor(qwen_path, grok_api_key)
        self.grok = GrokClient(grok_api_key) if grok_api_key else None
        self.HAS_GROK = grok_api_key is not None

    def execute(self, prompt: str, pdf_text: Optional[str] = None, route: str = "Hybrid") -> Tuple[Dict, Dict]:
        if not self.HAS_DISTILBERT:
            return self._execute_grok_only(prompt, pdf_text, route)

        dag = self._decompose(prompt, pdf_text)
        dag["original_prompt"] = prompt
        results = self._execute_parallel(dag, pdf_text, route)
        final_output = self._stitch_outputs(dag, results)
        return dag, {"final_output": final_output, **results}

    def _execute_grok_only(self, prompt: str, pdf_text: Optional[str] = None, route: str = "Cloud") -> Tuple[Dict, Dict]:
        if not self.HAS_GROK:
            return {"dag": {"nodes": []}}, {"error": "No models available"}
        try:
            output = self.grok.generate(prompt, max_tokens=512)
            return {
                "dag": {"nodes": [{"id": "n1", "task": prompt, "model": "grok"}]},
                "results": {"n1": output}
            }
        except Exception as e:
            return {"dag": {"nodes": []}}, {"error": str(e)}

    def _decompose(self, prompt: str, pdf_text: Optional[str] = None) -> Dict:
        # Try template matching first
        for template in self._get_templates():
            if re.search(template["pattern"], prompt, re.IGNORECASE):
                return self._apply_template(template, prompt)

        # Try hierarchical decomposition
        if len(prompt.split()) > 10:
            return self._hierarchical_decompose(prompt, pdf_text)

        # Default: Single task
        return {"dag": {"nodes": [{"id": "n1", "task": prompt, "model": "qwen"}]}}

    def _get_templates(self) -> List[Dict]:
        return [
            {
                "pattern": r"(summarize|extract.*from).*?(and|then).*?(write|draft|create)",
                "dag": {
                    "nodes": [
                        {"id": "n1", "task": "Summarize the input", "model": "qwen"},
                        {"id": "n2", "task": "Write the output based on the summary", "model": "qwen", "depends_on": ["n1"]}
                    ]
                }
            },
            {
                "pattern": r"(analyze|compare).*?(and|then).*?(explain|report)",
                "dag": {
                    "nodes": [
                        {"id": "n1", "task": "Analyze the input", "model": "qwen"},
                        {"id": "n2", "task": "Explain the analysis", "model": "qwen", "depends_on": ["n1"]}
                    ]
                }
            }
        ]

    def _apply_template(self, template: Dict, prompt: str) -> Dict:
        dag = copy.deepcopy(template["dag"])
        # Replace placeholders if needed
        for node in dag["nodes"]:
            node["task"] = node["task"].replace("{input}", prompt)
        return {"dag": dag}

    def _hierarchical_decompose(self, prompt: str, pdf_text: Optional[str] = None) -> Dict:
        sentences = sent_tokenize(prompt)
        dag = {"nodes": []}

        for i, sentence in enumerate(sentences):
            dag["nodes"].append({
                "id": f"n{i+1}",
                "task": sentence,
                "model": "qwen",
                "depends_on": []
            })

        # Add dependencies based on shared entities
        for i in range(len(sentences)):
            for j in range(i):
                if self._has_coreference(sentences[i], sentences[j]):
                    dag["nodes"][i]["depends_on"].append(f"n{j+1}")

        # Cluster similar sentences (simplified)
        if len(sentences) > 2:
            dag = self._cluster_tasks(dag)

        return {"dag": dag}

    def _has_coreference(self, sentence1: str, sentence2: str) -> bool:
        words1 = set(word.lower() for word in nltk.word_tokenize(sentence1) if word.isalnum())
        words2 = set(word.lower() for word in nltk.word_tokenize(sentence2) if word.isalnum())
        return len(words1 & words2) > 1

    def _cluster_tasks(self, dag: Dict) -> Dict:
        # Simplified clustering (replace with actual embeddings in production)
        sentences = [node["task"] for node in dag["nodes"]]
        # Mock embeddings (replace with DistilBERT in production)
        embeddings = np.random.rand(len(sentences), 768)
        clusters = AgglomerativeClustering(n_clusters=min(3, len(sentences)), affinity='cosine', linkage='average').fit_predict(embeddings)

        # Merge nodes in the same cluster
        new_dag = {"nodes": []}
        cluster_to_node = {}
        for i, node in enumerate(dag["nodes"]):
            cluster = clusters[i]
            if cluster not in cluster_to_node:
                cluster_to_node[cluster] = {
                    "id": f"cluster_{cluster}",
                    "task": node["task"],
                    "model": "qwen",
                    "depends_on": []
                }
                new_dag["nodes"].append(cluster_to_node[cluster])
            else:
                cluster_to_node[cluster]["task"] += f"\n\n{node['task']}"

        # Rebuild dependencies
        for node in new_dag["nodes"]:
            for old_node in dag["nodes"]:
                if old_node["task"] in node["task"]:
                    for dep in old_node.get("depends_on", []):
                        if dep not in node["depends_on"]:
                            node["depends_on"].append(dep)

        return new_dag

    def _execute_parallel(self, dag: Dict, pdf_text: Optional[str] = None, route: str = "Hybrid") -> Dict:
        results = {}
        futures = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit in topological order so parent futures exist when children are submitted
            sorted_tasks = self._topological_sort(dag["dag"]["nodes"])
            
            for task_id in sorted_tasks:
                node = next(t for t in dag["dag"]["nodes"] if t["id"] == task_id)
                
                def run_node(n, deps):
                    # Wait for dependencies to finish and gather context
                    context_parts = []
                    for d in deps:
                        res = futures[d].result()  # Wait for parent to finish
                        if isinstance(res, str):
                            context_parts.append(res)
                    
                    context = "\n\n".join(context_parts) if context_parts else None
                    return self.executor.execute(n, context, pdf_text, route)
                
                deps = node.get("depends_on", [])
                futures[task_id] = executor.submit(run_node, node, deps)

            for task_id, future in futures.items():
                try:
                    results[task_id] = future.result()
                except Exception as e:
                    results[task_id] = {"error": str(e)}

        return results

    def _stitch_outputs(self, dag: Dict, results: Dict) -> str:
        sorted_tasks = self._topological_sort(dag["dag"]["nodes"])
        final_parts = []

        for task_id in sorted_tasks:
            task = next(t for t in dag["dag"]["nodes"] if t["id"] == task_id)
            output = results[task_id]

            if isinstance(output, dict) and "error" in output:
                final_parts.append(f"Error in {task_id}: {output['error']}")
                continue

            # Resolve conflicts with dependencies
            for dep in task.get("depends_on", []):
                parent_output = results[dep]
                if self._contradicts(output, parent_output):
                    output = self._resolve_conflict(output, parent_output)

            final_parts.append(output)

        combined = "\n\n".join(final_parts)

        # Polish if Cloud route was used
        if dag.get("original_prompt") and any(node.get("route") == "Cloud" for node in dag["dag"]["nodes"]):
            combined = self._polish_output(combined, dag["original_prompt"])

        return combined

    def _topological_sort(self, nodes: List[Dict]) -> List[str]:
        in_degree = {node["id"]: 0 for node in nodes}
        graph = {node["id"]: [] for node in nodes}

        for node in nodes:
            for dep in node.get("depends_on", []):
                in_degree[node["id"]] += 1
                if dep in graph:
                    graph[dep].append(node["id"])

        queue = [node["id"] for node in nodes if in_degree[node["id"]] == 0]
        sorted_ids = []

        while queue:
            node_id = queue.pop(0)
            sorted_ids.append(node_id)
            for neighbor in graph.get(node_id, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return sorted_ids

    def _contradicts(self, output1: str, output2: str) -> bool:
        negations = ["not", "never", "opposite", "contradicts", "however", "but"]
        return any(neg in output1.lower() and neg in output2.lower() for neg in negations)

    def _resolve_conflict(self, output1: str, output2: str) -> str:
        if self.HAS_GROK:
            return self.grok.generate(
                f"Resolve conflict between these outputs:\nOutput 1: {output1}\nOutput 2: {output2}\nCombined:",
                max_tokens=256
            )
        return f"{output1}\n\nNote: Conflicts with: {output2}"

    def _polish_output(self, output: str, prompt: str) -> str:
        if self.HAS_GROK:
            return self.grok.generate(
                f"Refine this output to better match the original prompt:\nPrompt: {prompt}\nOutput: {output}\nRefined:",
                max_tokens=512
            )
        return output

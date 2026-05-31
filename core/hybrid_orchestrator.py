from typing import Dict, Tuple, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.grok_client import GrokClient
from core.task_executor import TaskExecutor
import re
import json
import nltk
import copy
import time
import math
from collections import defaultdict
from nltk.tokenize import sent_tokenize
from functools import lru_cache
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# ── Multi-language support (graceful import) ──────────────────────────────────
try:
    from classifier import detect_language, translate_to_english, decompose_prompt as _smart_decompose
    HAS_MULTILANG = True
except ImportError:
    HAS_MULTILANG = False
    def detect_language(text): return "en"
    def translate_to_english(text, lang): return text
    def _smart_decompose(prompt, lang="en"): return {"nodes": [{"id": "n1", "task": prompt, "model": "qwen", "route": "Hybrid", "depends_on": []}], "language": lang}

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
        """Execute a prompt through the orchestrator pipeline with full telemetry.
        
        Returns:
            (dag, results) where results includes 'final_output', 'times', 'retry_counts',
            and all individual task outputs keyed by node ID.
        """
        start_time = time.time()

        # ── Step 1: Language detection + translation ───────────────────────────
        lang = detect_language(prompt)
        original_lang = lang
        if lang != "en" and route != "Cloud":
            translated_prompt = translate_to_english(prompt, lang)
        else:
            translated_prompt = prompt

        # ── Step 2: Reset retry tracker for this execution ────────────────────
        self.executor.reset_retry_counts()

        # ── Step 3: Decompose + execute ───────────────────────────────────────
        if not self.HAS_DISTILBERT:
            dag, raw_results = self._execute_grok_only(translated_prompt, pdf_text, route)
        else:
            dag = self._decompose(translated_prompt, pdf_text, lang=lang)
            dag["original_prompt"] = prompt
            dag["language"] = lang
            raw_results = self._execute_parallel(dag, pdf_text, route)

        final_output = self._stitch_outputs(dag, raw_results, original_prompt=prompt)
        edge_time = time.time() - start_time

        # ── Step 4: Estimate traditional (sequential cloud) time ──────────────
        total_words = sum(len(node["task"].split()) for node in dag.get("dag", dag).get("nodes", []))
        traditional_time = total_words / 20  # Grok processes ~20 tokens/sec sequentially
        savings_pct = ((traditional_time - edge_time) / traditional_time * 100) if traditional_time > 0 else 0

        results = {
            "final_output": final_output,
            "times": {
                "edge_ai": round(edge_time, 3),
                "traditional": round(traditional_time, 3),
                "savings": round(traditional_time - edge_time, 3),
                "savings_percent": round(savings_pct, 1),
            },
            "retry_counts": self.executor.get_retry_counts(),
            "detected_language": original_lang,
            **raw_results,
        }
        return dag, results

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

    def _decompose(self, prompt: str, pdf_text: Optional[str] = None, lang: str = "en") -> Dict:
        """Smart universal decomposition — tries template matching, then smart NLP, then hierarchical."""
        # Try template matching first (fastest)
        for template in self._get_templates():
            if re.search(template["pattern"], prompt, re.IGNORECASE):
                dag = self._apply_template(template, prompt)
                dag["language"] = lang
                return dag

        # Use smart multi-language decomposition from classifier.py
        if HAS_MULTILANG:
            smart_dag = _smart_decompose(prompt, lang=lang)
            if len(smart_dag.get("nodes", [])) > 1:
                return {"dag": smart_dag, "language": lang}

        # Hierarchical decomposition for longer prompts
        if len(prompt.split()) > 10:
            dag = self._hierarchical_decompose(prompt, pdf_text)
            dag["language"] = lang
            return dag

        # Default: Single task
        return {"dag": {"nodes": [{"id": "n1", "task": prompt, "model": "qwen", "route": "Hybrid", "depends_on": []}]}, "language": lang}

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
        """Execute DAG nodes in topological order, passing full dependency context to each child."""
        results = {}
        futures = {}

        with ThreadPoolExecutor(max_workers=4) as executor:
            sorted_tasks = self._topological_sort(dag["dag"]["nodes"])

            for task_id in sorted_tasks:
                node = next(t for t in dag["dag"]["nodes"] if t["id"] == task_id)

                def run_node(n, deps):
                    # Build rich context from ALL dependency outputs
                    context_parts = []
                    for dep_id in deps:
                        dep_res = futures[dep_id].result()  # blocks until parent done
                        if isinstance(dep_res, str) and dep_res.strip():
                            # Find the dependency task description for labelling
                            dep_node = next(
                                (x for x in dag["dag"]["nodes"] if x["id"] == dep_id), None
                            )
                            dep_desc = dep_node.get("task", dep_id)[:80] if dep_node else dep_id
                            context_parts.append(
                                f"[Step {dep_id} — {dep_desc}]\n{dep_res[:1500]}"
                            )

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

    # ══════════════════════════════════════════════════════════════════════════
    # INTELLIGENT OUTPUT STITCHING
    # ══════════════════════════════════════════════════════════════════════════

    def _stitch_outputs(self, dag: Dict, results: Dict, original_prompt: str = "") -> str:
        """
        Intelligently stitch task outputs into ONE coherent answer.

        Strategy (with fallback chain):
          1. Single task → return directly (no stitching needed).
          2. Multiple tasks + Grok available → Grok synthesizes everything.
          3. Multiple tasks + only Qwen → Qwen synthesizes.
          4. No LLM → topological smart concatenation with section headers.
        """
        nodes = dag.get("dag", dag).get("nodes", [])

        # ── Case 1: Only one task — nothing to stitch ─────────────────────────
        if len(nodes) <= 1:
            single_id = nodes[0]["id"] if nodes else "n1"
            out = results.get(single_id, "")
            return out if isinstance(out, str) else str(out)

        # ── Collect task details (with truncation to keep tokens manageable) ──
        task_details = []
        sorted_ids = self._topological_sort(nodes)
        for task_id in sorted_ids:
            node = next((n for n in nodes if n["id"] == task_id), {})
            output = results.get(task_id, "")
            if isinstance(output, dict):
                output = output.get("error", str(output))

            # Gather dependency outputs for context labelling
            dep_summaries = []
            for dep_id in node.get("depends_on", []):
                dep_node = next((n for n in nodes if n["id"] == dep_id), None)
                dep_desc = dep_node.get("task", dep_id)[:60] if dep_node else dep_id
                dep_out  = results.get(dep_id, "")
                if isinstance(dep_out, str) and dep_out.strip():
                    dep_summaries.append(f"{dep_desc}: {dep_out[:300]}")

            task_details.append({
                "id":           task_id,
                "description":  node.get("task", task_id),
                "output":       self._truncate_for_synthesis(output),
                "dependencies": "\n".join(dep_summaries) if dep_summaries else "None",
            })

        synthesis_prompt = self._create_synthesis_prompt(original_prompt, task_details)

        # ── Case 2: Grok synthesis (best quality) ─────────────────────────────
        if self.HAS_GROK and self.grok:
            try:
                result = self.grok.generate(
                    synthesis_prompt,
                    max_tokens=2048,
                    temperature=0.3,
                )
                if result and not result.startswith("⚠️"):
                    return result
            except Exception as e:
                print(f"[orchestrator] Grok synthesis failed: {e}")

        # ── Case 3: Qwen synthesis (fallback) ────────────────────────────────
        if getattr(self.executor, "HAS_QWEN", False):
            try:
                out = self.executor._run_qwen(synthesis_prompt[:3000])  # Qwen has smaller ctx
                if out and not out.startswith(("⚠️", "Qwen error")):
                    return out
            except Exception as e:
                print(f"[orchestrator] Qwen synthesis failed: {e}")

        # ── Case 4: Smart concatenation (ultimate fallback) ───────────────────
        return self._smart_concatenation(nodes, results, sorted_ids)

    def _create_synthesis_prompt(self, original_prompt: str, task_details: list) -> str:
        """
        Build a detailed prompt that tells Grok/Qwen exactly how to synthesize
        multiple task outputs into a single, human-quality answer.
        """
        tasks_block = ""
        for i, task in enumerate(task_details, 1):
            tasks_block += f"""
**Task {i}: {task['description']}**
- Dependency context: {task['dependencies']}
- Output: {task['output']}
---"""

        return f"""You are an expert analyst. Synthesize the following task outputs into ONE coherent, professional answer that directly addresses the user's original request.

ORIGINAL USER REQUEST:
{original_prompt}

TASK OUTPUTS:
{tasks_block}

SYNTHESIS RULES:
1. Address the ORIGINAL REQUEST completely — that is the only thing that matters.
2. Combine all relevant information with logical flow: introduction → body → conclusion.
3. Use Markdown formatting: ## for sections, **bold** for key points, - for bullet lists.
4. Remove all redundancy — never repeat the same point twice.
5. Resolve any contradictions between task outputs using sound reasoning.
6. Do NOT mention "tasks", "outputs", "steps", or any internal pipeline terminology.
7. Do NOT start with "Here is..." or "Certainly!" — begin directly with the answer.
8. Write as a single intelligent voice, not as a list of sections from different sources.

SYNTHESIZED ANSWER:"""

    def _truncate_for_synthesis(self, text: str, max_chars: int = 2000) -> str:
        """Truncate a task output to keep the synthesis prompt within token limits."""
        if not text or len(text) <= max_chars:
            return text
        return text[:max_chars] + f"\n…[truncated {len(text)-max_chars} chars]"

    def _smart_concatenation(self, nodes: list, results: dict, sorted_ids: list) -> str:
        """
        Fallback when no LLM is available: topological concatenation with section headers.
        Skips a task's output if it already contains the full content of a dependency.
        """
        final_parts = []
        seen_content: set = set()

        for task_id in sorted_ids:
            node   = next((n for n in nodes if n["id"] == task_id), {})
            output = results.get(task_id, "")
            if isinstance(output, dict):
                output = output.get("error", str(output))
            if not output or not output.strip():
                continue

            # Deduplicate: skip if this output is almost identical to something already added
            output_sig = output.strip()[:200]
            if output_sig in seen_content:
                continue
            seen_content.add(output_sig)

            task_desc = node.get("task", task_id)
            # Only add a header if the output doesn't already open with the task description
            if task_desc.lower()[:30] not in output.lower()[:100]:
                final_parts.append(f"### {task_desc}\n\n{output}")
            else:
                final_parts.append(output)

        return "\n\n".join(final_parts)

    # ══════════════════════════════════════════════════════════════════════════
    # TOPOLOGICAL SORT + LEGACY CONFLICT HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    def _topological_sort(self, nodes: List[Dict]) -> List[str]:
        """Kahn's algorithm — returns node IDs in dependency order."""
        in_degree = {node["id"]: 0 for node in nodes}
        graph     = {node["id"]: [] for node in nodes}

        for node in nodes:
            for dep in node.get("depends_on", []):
                in_degree[node["id"]] += 1
                if dep in graph:
                    graph[dep].append(node["id"])

        queue      = [node["id"] for node in nodes if in_degree[node["id"]] == 0]
        sorted_ids = []
        while queue:
            node_id = queue.pop(0)
            sorted_ids.append(node_id)
            for neighbor in graph.get(node_id, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Append any nodes not reached (e.g. cycles) at the end
        for node in nodes:
            if node["id"] not in sorted_ids:
                sorted_ids.append(node["id"])

        return sorted_ids

    def _contradicts(self, output1: str, output2: str) -> bool:
        negations = ["not", "never", "opposite", "contradicts", "however", "but"]
        return any(neg in output1.lower() and neg in output2.lower() for neg in negations)

    def _resolve_conflict(self, output1: str, output2: str) -> str:
        if self.HAS_GROK and self.grok:
            return self.grok.generate(
                f"Resolve the contradiction between these two statements and give one unified answer:\n"
                f"Statement A: {output1[:500]}\nStatement B: {output2[:500]}\nUnified:",
                max_tokens=300,
            )
        return f"{output1}\n\n*(Note: possible conflict with an earlier step.)*"

    def _polish_output(self, output: str, prompt: str) -> str:
        """Legacy polish hook — now superseded by _stitch_outputs synthesis."""
        if self.HAS_GROK and self.grok:
            return self.grok.generate(
                f"Refine this output to better match the original prompt.\n"
                f"Prompt: {prompt}\nOutput: {output[:1000]}\nRefined:",
                max_tokens=512,
            )
        return output

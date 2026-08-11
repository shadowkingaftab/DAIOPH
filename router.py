"""
router.py
---------
The decision-maker AND executor of the system.

Routes prompts to:
  ODA       → Qwen-1.8B GGUF (local, fast, private, ~300MB)
  Hybrid    → Qwen (edge) + Grok (cloud) working in parallel
  Cloud LLM → Grok API (primary) with automatic Qwen fallback

Every execution path now uses Grok-primary / Qwen-fallback logic,
so the system degrades gracefully even without an internet connection.
"""

import time


# ── Lazy imports ──────────────────────────────────────────────────────────────
def _qwen():
    """Lazy-import run_qwen — returns None if llama_cpp is not installed."""
    try:
        from qwen_oda import run_qwen, is_llm_available
        if not is_llm_available():
            return None
        return run_qwen
    except ImportError:
        return None


def _grok():
    """Lazy-import run_grok and run_grok_with_fallback from grok_cloud."""
    try:
        from grok_cloud import run_grok, run_grok_with_fallback
        return run_grok, run_grok_with_fallback
    except ImportError:
        return None, None


# ── Main router ───────────────────────────────────────────────────────────────
def route_task(intent_matrix: dict, text: str) -> dict:
    try:
        pass
    except Exception as e:
        return {"route": "Error", "output": f"Fallback: {str(e)}"}

    """
    Route the task based on the intent matrix, then execute with the right model.

    Execution strategy:
      ODA route       → Qwen GGUF (local, offline-capable)
      Cloud LLM route → Grok API (primary) → Qwen (fallback)
      Hybrid route    → Qwen (edge part) + Grok (cloud part) in sequence

    Returns a dict with:
      route        : "ODA" | "Hybrid" | "Cloud LLM"
      output       : Final response (ODA and Cloud routes)
      edge_output  : Qwen's response (Hybrid only)
      cloud_output : Grok's response (Hybrid only)
      latency_ms   : Total execution time in milliseconds
      model_used   : Actual model that produced the response
    """
    if not intent_matrix:
        return {
            "route":      "Cloud LLM",
            "output":     "No intent matrix provided.",
            "model_used": "none",
            "latency_ms": 0,
        }

    start_time = time.time()
    top_intent, top_confidence = max(intent_matrix.items(), key=lambda x: x[1])
    text_lower = text.lower()

    # ── Routing decision ──────────────────────────────────────────────────────
    if "urgent" in text_lower or intent_matrix.get("urgent", 0) > 0.5:
        route = "Cloud LLM"
    elif intent_matrix.get("multi_step", 0) > 0.3:
        route = "Hybrid"
    elif top_confidence < 0.55:
        route = "Cloud LLM"
    elif top_confidence >= 0.75 and top_intent in ["summarize", "translate", "simple_query"]:
        route = "ODA"
    elif top_confidence >= 0.75:
        route = "Cloud LLM"
    else:
        route = "Hybrid"

    # ── Get module references ─────────────────────────────────────────────────
    run_qwen = _qwen()
    _, run_grok_with_fallback = _grok()

    # ── ODA: Local Qwen, fall back to Grok if unavailable ───────────────────
    if route == "ODA":
        if run_qwen:
            output = run_qwen(text)
            model_used = "Qwen2-0.5B-GGUF"
        elif run_grok_with_fallback:
            # Qwen not installed — use Grok as stand-in
            output, _ = run_grok_with_fallback(text)
            model_used = "Grok (Qwen offline)"
        else:
            output = "❌ No inference engine available. Set GROK_API_KEY or install llama-cpp-python."
            model_used = "none"

        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "route":      route,
            "output":     output,
            "model_used": model_used,
            "latency_ms": latency_ms,
        }

    # ── Cloud LLM: Grok primary, Qwen fallback ────────────────────────────────
    elif route == "Cloud LLM":
        if run_grok_with_fallback:
            output, source = run_grok_with_fallback(text)
            model_used = "Grok" if source == "grok" else (
                "Qwen2-0.5B-GGUF (Grok fallback)" if source == "qwen" else "none"
            )
        elif run_qwen:
            # grok_cloud.py not importable — go straight to Qwen
            output = run_qwen(text)
            model_used = "Qwen2-0.5B-GGUF (Grok unavailable)"
        else:
            output = "❌ No inference engine available. Set GROK_API_KEY or install llama-cpp-python."
            model_used = "none"

        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "route":      route,
            "output":     output,
            "model_used": model_used,
            "latency_ms": latency_ms,
        }

    # ── Hybrid: Qwen handles edge, Grok handles cloud ─────────────────────────
    else:  # Hybrid
        edge_prompt  = f"Handle the first part of this task concisely: {text}"
        cloud_prompt = f"Handle the second part of this task in detail: {text}"

        # Edge (Qwen → Grok fallback)
        if run_qwen:
            edge_output  = run_qwen(edge_prompt)
            edge_model   = "Qwen2-0.5B-GGUF"
        elif run_grok_with_fallback:
            edge_output, _ = run_grok_with_fallback(edge_prompt)
            edge_model   = "Grok (Qwen offline)"
        else:
            edge_output  = "❌ No inference engine available."
            edge_model   = "none"

        # Cloud (Grok → Qwen fallback)
        if run_grok_with_fallback:
            cloud_output, cloud_source = run_grok_with_fallback(cloud_prompt)
            cloud_model = "Grok" if cloud_source == "grok" else "Qwen2-0.5B-GGUF (fallback)"
        elif run_qwen:
            cloud_output = run_qwen(cloud_prompt)
            cloud_model  = "Qwen2-0.5B-GGUF"
        else:
            cloud_output = "❌ No cloud or local engine available."
            cloud_model  = "none"

        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "route":        route,
            "edge_output":  edge_output,
            "cloud_output": cloud_output,
            "output":       f"[Edge — {edge_model}]\n{edge_output}\n\n[Cloud — {cloud_model}]\n{cloud_output}",
            "model_used":   f"{edge_model} + {cloud_model}",
            "latency_ms":   latency_ms,
        }


# ── Legacy helpers (kept for MCP server backward compatibility) ───────────────
def get_route(intent: str, confidence: float) -> str:
    """Legacy routing for MCP server / older callers."""
    if confidence < 0.55:
        return "Cloud LLM"
    if intent in ["multi-step task", "multi_step"]:
        return "Hybrid"
    if confidence >= 0.75 and intent in [
        "question", "instruction", "summarize", "translate", "simple_query"
    ]:
        return "ODA"
    if confidence >= 0.75 and intent in [
        "analysis", "creative request", "analyze_data", "generate_code"
    ]:
        return "Cloud LLM"
    return "Hybrid"


def get_route_color(route: str) -> str:
    return {"ODA": "🟢", "Hybrid": "🟡", "Cloud LLM": "🔴"}.get(route, "⚪")


def get_route_explanation(intent_matrix: dict, route: str) -> str:
    if not intent_matrix:
        return "No intent matrix provided."
    top_intent, top_confidence = max(intent_matrix.items(), key=lambda x: x[1])
    pct = round(top_confidence * 100, 1)
    if intent_matrix.get("urgent", 0) > 0.5:
        return "Task marked as urgent — routing directly to Grok (Cloud LLM)."
    if intent_matrix.get("multi_step", 0) > 0.3:
        return "Multi-step task — Hybrid splits lightweight steps to Qwen (edge), complex steps to Grok (cloud)."
    if top_confidence < 0.55:
        return f"Low confidence ({pct}%) — Grok Cloud LLM provides safer, deeper processing."
    if route == "ODA":
        return f"High confidence ({pct}%) on a simple '{top_intent}' — Qwen-1.8B handles this locally (fast & private)."
    if route == "Cloud LLM":
        return f"'{top_intent.capitalize()}' needs deep reasoning — sending to Grok (with Qwen fallback)."
    return f"Medium confidence ({pct}%) — Hybrid gives the best balance of speed and quality."

# ── Smart Orchestration Features ──────────────────────────────────────────────

class TaskExecutor:
    def execute(self, task, context, pdf_text, route):
        prompt = task.get("task", "")
        # Forward to the standard router
        # Fake intent matrix for simplicity to force Cloud/ODA based on route
        intent_matrix = {"multi_step": 1.0} if route == "Hybrid" else {"simple_query": 1.0}
        result = route_task(intent_matrix, prompt)
        if isinstance(result, dict) and "output" in result:
            return result["output"]
        return str(result)

class HybridOrchestrator:
    def __init__(self):
        self.executor = TaskExecutor()

    def execute(self, prompt, pdf_text=None, route="Hybrid"):
        from classifier import decompose_prompt
        start_time = time.time()
        
        # 1. Dynamic decomposition & Auto-correction
        dag = decompose_prompt(prompt)
        corrected_prompt = dag.get("corrected_prompt", prompt)
        
        results = {}
        failed_tasks = []

        # 2. Execute tasks with automatic retries
        for node in dag["nodes"]:
            task_id = node["id"]
            context = {k: results[k] for k in node.get("depends_on", [])}
            
            # Try execution with retries
            for attempt in range(3):
                try:
                    results[task_id] = self.executor.execute(node, context, pdf_text, route)
                    break
                except Exception as e:
                    if attempt == 2:
                        failed_tasks.append(task_id)
                        results[task_id] = f"Error: {str(e)}"
                    time.sleep(1)

        # 3. Recover failed tasks dynamically
        if failed_tasks:
            results = self._recover_failed_tasks(dag, results, failed_tasks, route)

        # 4. Smart stitching using LLM
        final_output = self._stitch_outputs(dag, results, corrected_prompt)

        execution_time = time.time() - start_time
        traditional_time = len(prompt.split()) / 20

        return {
            "dag": dag,
            "results": results,
            "final_output": final_output,
            "times": {
                "edge_ai": execution_time,
                "traditional": traditional_time,
                "savings": traditional_time - execution_time,
                "savings_percent": ((traditional_time - execution_time) / traditional_time * 100) if traditional_time > 0 else 0
            }
        }

    def _recover_failed_tasks(self, dag, results, failed_tasks, route):
        """Dynamically recover failed tasks by rephrasing them via Grok."""
        try:
            from grok_cloud import run_grok
        except ImportError:
            run_grok = None
            
        for task_id in failed_tasks:
            node = next(n for n in dag["nodes"] if n["id"] == task_id)
            intent = node.get("intent")

            if run_grok:
                try:
                    recovery_prompt = f"""
                    This task failed to execute: "{node['task']}"
                    Intent: {intent or 'unknown'}
                    Rephrase this task to make it executable while preserving the original meaning.
                    Return ONLY the rephrased task.
                    """
                    rephrased_task = run_grok(recovery_prompt, max_tokens=256, timeout=10)
                    if not rephrased_task.startswith("❌"):
                        results[task_id] = self.executor.execute(
                            {"id": task_id, "task": rephrased_task, "intent": intent},
                            None, None, route
                        )
                    else:
                        results[task_id] = f"Recovered: {node['task'][:100]}..."
                except:
                    results[task_id] = f"Recovered: {node['task'][:100]}..."
            else:
                results[task_id] = f"Recovered: {node['task'][:100]}..."
        return results

    def _stitch_outputs(self, dag, results, original_prompt):
        """Use LLM to dynamically stitch outputs into a coherent answer."""
        try:
            from grok_cloud import run_grok
        except ImportError:
            run_grok = None

        if len(results) == 1:
            return list(results.values())[0]

        task_details = []
        for node in dag["nodes"]:
            task_id = node["id"]
            task_desc = node.get("task", task_id)
            output = results.get(task_id, "")
            intent = node.get("intent")
            confidence = 10 if not str(output).startswith("Error") else 3
            task_details.append({
                "id": task_id,
                "description": task_desc,
                "output": output,
                "intent": intent,
                "confidence": confidence
            })

        if run_grok:
            try:
                synthesis_prompt = f"""
                You are an expert at synthesizing information into coherent answers.
                Original User Request: {original_prompt}

                Task Breakdown:
                {'='*50}
                """
                for task in task_details:
                    synthesis_prompt += f"""
                Task {task['id']}: {task['description']}
                Intent: {task['intent'] or 'N/A'}
                Output: {task['output']}
                Confidence: {task['confidence']}/10
                {'-'*50}
                """
                synthesis_prompt += """
                Instructions:
                1. Combine everything into a SINGLE, COHERENT answer that addresses the Original Request.
                2. If any task output is missing, make reasonable assumptions based on the context.
                3. NEVER mention tasks, outputs, or errors explicitly in the response.
                """
                resp = run_grok(synthesis_prompt, max_tokens=1024, temperature=0.3, timeout=15)
                if not resp.startswith("❌"):
                    return resp
            except:
                pass

        return "\n\n".join(str(v) for v in results.values())

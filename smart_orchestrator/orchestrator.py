from typing import List, Dict, Tuple, Optional
from utils.prompt_decomposer import SmartPromptDecomposer
from llama_cpp import Llama
import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class LLMOrchestrator:
    def __init__(self, qwen_model_path: str, grok_api_key: str):
        self.qwen = Llama(model_path=qwen_model_path, n_ctx=4096, n_threads=8)
        self.grok_api_key = grok_api_key
        self.decomposer = SmartPromptDecomposer(api_key=grok_api_key)
        self.task_capabilities = {
            "code_generation": True,
            "math": True,
            "creative_writing": False,
            "simplification": False,
            "large_context": True
        }
        self.feedback_db = []

    def detect_capabilities(self) -> Dict:
        """Auto-detects what each LLM can handle"""
        test_prompts = {
            "code_generation": "Write a Python function to reverse a string",
            "math": "Calculate the square root of 144",
            "creative_writing": "Write a haiku about the ocean",
            "simplification": "Explain quantum physics to a 5-year-old"
        }

        capabilities = {}
        for name, prompt in test_prompts.items():
            try:
                if name in ["code_generation", "math"]:
                    result = self._execute_cloud_task({"task": prompt})
                else:
                    result = self.qwen(prompt, max_tokens=256)["choices"][0]["text"]

                if len(result) > 50:  # Simple validation
                    capabilities[name] = True
                else:
                    capabilities[name] = False
            except:
                capabilities[name] = False

        self.task_capabilities.update(capabilities)
        return capabilities

    def execute(self, prompt: str) -> Tuple[str, Dict]:
        # Step 1: Decompose prompt
        decomposition = self.decomposer.decompose(prompt)
        if not decomposition:
            return "I couldn't decompose that prompt. Please try rephrasing.", {"error": "decomposition_failed"}

        # Step 2: Analyze capabilities needed
        cloud_tasks = []
        device_tasks = []
        task_results = {}
        task_visualization = {
            "original_prompt": prompt,
            "micro_tasks": decomposition["micro_tasks"],
            "routing": {"cloud": [], "device": []},
            "results": {},
            "execution_plan": []
        }

        # Step 3: Route tasks based on capabilities
        for task in decomposition["micro_tasks"]:
            needs = task.get("capabilities_needed", [])
            can_run_device = all(not self.task_capabilities.get(c, True) for c in needs)

            if can_run_device and not any(c in needs for c in ["code_generation", "math"]):
                device_tasks.append(task)
                task_visualization["routing"]["device"].append(task["id"])
            else:
                cloud_tasks.append(task)
                task_visualization["routing"]["cloud"].append(task["id"])

        import time

        # Step 4: Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Device tasks (synchronous)
            for task in device_tasks:
                start_time = time.time()
                future = executor.submit(self._execute_device_task, task)
                task_visualization["execution_plan"].append({
                    "task_id": task["id"],
                    "status": "queued",
                    "executor": "device"
                })
                task_results[f"device_{task['id']}"] = (future, start_time)

            # Cloud tasks (asynchronous)
            cloud_futures = {}
            for task in cloud_tasks:
                start_time = time.time()
                future = executor.submit(self.execute_with_fallback, task)
                cloud_futures[future] = (task["id"], start_time)
                task_visualization["execution_plan"].append({
                    "task_id": task["id"],
                    "status": "queued",
                    "executor": "cloud"
                })

            # Collect cloud results
            for future in as_completed(cloud_futures):
                task_id, start_time = cloud_futures[future]
                exec_time = time.time() - start_time
                # Update status in plan
                for plan in task_visualization["execution_plan"]:
                    if plan["task_id"] == task_id and plan["executor"] == "cloud":
                        plan["status"] = "completed"
                        plan["execution_time"] = exec_time
                        
                try:
                    result = future.result()
                    task_results[f"cloud_{task_id}"] = result
                    task_visualization["results"][f"cloud_{task_id}"] = {
                        "status": "completed",
                        "result": result
                    }
                except Exception as e:
                    task_visualization["results"][f"cloud_{task_id}"] = {
                        "status": "failed",
                        "error": str(e)
                    }

        # Step 5: Process device results
        for task in device_tasks:
            future, start_time = task_results[f"device_{task['id']}"]
            exec_time = time.time() - start_time
            # Update status in plan
            for plan in task_visualization["execution_plan"]:
                if plan["task_id"] == task["id"] and plan["executor"] == "device":
                    plan["status"] = "completed"
                    plan["execution_time"] = exec_time
                    
            try:
                result = future.result()
                task_results[f"device_{task['id']}"] = result
                task_visualization["results"][f"device_{task['id']}"] = {
                    "status": "completed",
                    "result": result
                }
            except Exception as e:
                task_visualization["results"][f"device_{task['id']}"] = {
                    "status": "failed",
                    "error": str(e)
                }

        # Step 6: Aggregate results
        final_response = self._smart_aggregate_results(task_results, decomposition)
        return final_response, task_visualization

    def execute_with_fallback(self, task: Dict) -> str:
        """Execute with cloud fallback to device"""
        try:
            return self._execute_cloud_task(task)
        except Exception as e:
            print(f"Cloud failed for Task {task['id']}, falling back to device: {e}")
            return self._execute_device_task(task)

    def execute_batch(self, prompts: List[str]) -> List[Tuple[str, Dict]]:
        """Process multiple prompts efficiently"""
        results = []
        for prompt in prompts:
            result, visualization = self.execute(prompt)
            results.append((result, visualization))
        return results
        
    def save_feedback(self, task_id: int, rating: int, comment: str):
        """Store user feedback to improve routing"""
        self.feedback_db.append({
            "task_id": task_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        })

    def _execute_device_task(self, task: Dict) -> str:
        """Execute task on-device Qwen"""
        try:
            return self.qwen(
                prompt=task["task"],
                max_tokens=512,
                temperature=0.7
            )["choices"][0]["text"].strip()
        except Exception as e:
            raise RuntimeError(f"Device execution failed: {str(e)}")

    def _execute_cloud_task(self, task: Dict) -> str:
        """Execute task on cloud Grok"""
        try:
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "messages": [{"role": "user", "content": task["task"]}],
                "model": "grok-1",
                "max_tokens": 512
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Cloud execution failed: {str(e)}")

    def _smart_aggregate_results(self, results: Dict, decomposition: Dict) -> str:
        """Intelligent result merging based on task dependencies"""
        sorted_results = sorted(results.items(), key=lambda x: x[0].split('_')[-1])

        final_parts = []
        for key, result in sorted_results:
            if isinstance(result, Exception):
                final_parts.append(f"[Task failed: {str(result)}]")
                continue
            
            # Since task_results might store tuple (future, start_time) initially,
            # but we replace it with `result = future.result()` before this function.
            # Only successful results or exception strings remain here.
            
            if key.startswith("device_"):
                final_parts.append(f"📱 {result}")
            else:
                final_parts.append(f"☁️ {result}")

        return "\n\n".join(final_parts)

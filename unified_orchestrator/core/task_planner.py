import json
import re
from typing import Dict
import sys
import os

# Ensure root directory is in path to import the existing DistilBERT classifier
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from classifier import classify_prompt

class TaskPlanner:
    def __init__(self, model_path: str = None):
        # We leverage the local DistilBERT classifier for bifurcation
        pass

    def plan(self, prompt: str, pdf_text: str = None) -> Dict:
        """Generate DAG using DistilBERT Zero-Shot Classification for bifurcation."""
        
        # 1. Use DistilBERT to classify the intent
        try:
            classification = classify_prompt(prompt)
            is_multi_step = classification["is_multi_step"]
        except Exception:
            is_multi_step = False
            
        # 2. Check for explicit sequential keywords (e.g., "First X, then Y")
        sequential_match = re.search(
            r'(First|Initially|Start by|Step \d+:)\s*(.*?)\s*(Then|Next|After that|Step \d+:)\s*(.*)',
            prompt,
            re.IGNORECASE | re.DOTALL
        )
        
        if sequential_match:
            task1 = sequential_match.group(2).strip()
            task2 = sequential_match.group(4).strip()
            return {
                "dag": {
                    "nodes": [
                        {"id": "n1", "task": task1, "model": "qwen"},
                        {"id": "n2", "task": task2, "model": "qwen", "depends_on": ["n1"]}
                    ]
                }
            }
            
        # 3. If DistilBERT flags it as multi_step but no explicit 'First/Then' keywords were found
        if is_multi_step:
            # Fallback split logic using 'and' or 'and then'
            parts = re.split(r'\b(and then|and)\b', prompt, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) >= 3:
                task1 = parts[0].strip()
                task2 = parts[2].strip()
                return {
                    "dag": {
                        "nodes": [
                            {"id": "n1", "task": task1, "model": "qwen"},
                            {"id": "n2", "task": task2, "model": "qwen", "depends_on": ["n1"]}
                        ]
                    }
                }
                
        # 4. Fallback: Single Task execution for simple queries
        return {"dag": {"nodes": [{"id": "n1", "task": prompt, "model": "qwen"}]}}

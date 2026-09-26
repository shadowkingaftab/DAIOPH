import json
from typing import List, Dict, Optional
from openai import OpenAI  # Or use Bartender SDK if available

class SmartPromptDecomposer:
    def __init__(self, api_key: str, model: str = "bartender"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.decomposition_prompt = """
        You are an expert prompt decomposer. Break down complex prompts into atomic, executable micro-tasks.

        Instructions:
        1. Identify the core requirements
        2. Split into independent sub-tasks
        3. Preserve semantic meaning
        4. Mark dependencies between tasks
        5. Indicate required capabilities for each task

        Example Input:
        "Write a Python function to implement BERT and calculate its F1 score on the SST-2 dataset, then explain the architecture in simple terms."

        Example Output:
        {
            "original_prompt": "Write a Python function to implement BERT and calculate its F1 score on the SST-2 dataset, then explain the architecture in simple terms.",
            "micro_tasks": [
                {
                    "id": 1,
                    "task": "Write a Python class to implement a BERT model for text classification",
                    "capabilities_needed": ["code_generation", "python"],
                    "dependencies": []
                },
                {
                    "id": 2,
                    "task": "Implement F1 score calculation for model evaluation",
                    "capabilities_needed": ["code_generation", "math"],
                    "dependencies": [1]
                },
                {
                    "id": 3,
                    "task": "Explain the BERT architecture in simple terms for a 5-year-old",
                    "capabilities_needed": ["creative_writing", "simplification"],
                    "dependencies": []
                }
            ],
            "capability_analysis": {
                "requires_cloud": ["code_generation", "math"],
                "requires_device": ["creative_writing"]
            }
        }
        """

    def decompose(self, prompt: str) -> Optional[Dict]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful prompt decomposer."},
                    {"role": "user", "content": f"{self.decomposition_prompt}\n\nPROMPT TO DECOMPOSE:\n{prompt}"}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Decomposition failed: {str(e)}")
            return None

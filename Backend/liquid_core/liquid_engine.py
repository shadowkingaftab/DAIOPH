from models.liquid_neural_networks.lnn_intent_classifier import LiquidIntentClassifier
from memory.short_term_memory import ShortTermMemory
import psutil
import os

class LiquidEngine:
    def __init__(self):
        self.classifier = LiquidIntentClassifier()
        self.memory = ShortTermMemory()
        self.hardware_specs = self._detect_hardware()
        self.classifier.load()
        self.execution_count = 0
        self.RETRAIN_INTERVAL = 10  # Retrain every 10 prompts

    def _detect_hardware(self):
        """Detect CPU cores, RAM, and GPU availability."""
        specs = {
            "cpu_cores": psutil.cpu_count(logical=False),
            "ram_gb": psutil.virtual_memory().total / (1024 ** 3),
            "gpu_available": False
        }
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            specs["gpu_available"] = len(gpus) > 0
            specs["gpu_name"] = gpus[0].name if gpus else None
        except:
            pass
        return specs

    def process_prompt(self, prompt):
        intent = self.classifier.classify(prompt)
        self.memory.store(prompt, intent)
        self.classifier.update(prompt, intent)

        # Auto-retrain every N executions
        self.execution_count += 1
        if self.execution_count % self.RETRAIN_INTERVAL == 0:
            self.train_from_memory()
            print(f"[LiquidEngine] Retrained after {self.execution_count} executions")

        return intent

    def train_from_memory(self, limit=100):
        """Retrain classifier using recent interactions."""
        interactions = self.memory.get_recent(limit)
        if interactions:
            prompts, intents = zip(*interactions)
            self.classifier.train(prompts, intents)
            print(f"[LiquidEngine] Retrained with {len(interactions)} interactions")

    def get_hardware_specs(self):
        return self.hardware_specs
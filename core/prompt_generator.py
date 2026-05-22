from core.task_executor import _resolve_model_path

try:
    from llama_cpp import Llama
    HAS_LLAMA = True
except ImportError:
    HAS_LLAMA = False

class PromptGenerator:
    def __init__(self, model_path: str):
        if HAS_LLAMA:
            resolved_path = _resolve_model_path(model_path)
            self.llm = Llama(
                model_path=resolved_path,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0
            )
        else:
            self.llm = None

    def generate(self) -> str:
        """Generate a random test prompt."""
        if not HAS_LLAMA:
            return "First, summarize the key benefits of Edge AI. Then, provide a real-world use case where hybrid cloud-edge architectures outshine pure cloud."
            
        prompt = """
        Generate a unique, complex prompt for testing an AI orchestration system.
        Requirements:
        1. Include 2-3 sequential steps (e.g., "First X, then Y").
        2. Mix creative and analytical tasks.
        3. Be realistic and human-like.
        4. Test both on-device and cloud capabilities.
        Example: "First, analyze this dataset of customer reviews. Then, write a report with key insights and recommendations."
        """
        output = self.llm(
            prompt=prompt,
            max_tokens=150,
            temperature=0.9
        )["choices"][0]["text"].strip()
        return output

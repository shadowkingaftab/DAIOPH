from llama_cpp import Llama

class PromptGenerator:
    def __init__(self, model_path: str):
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=2,  # Reduced for Streamlit Cloud
                n_gpu_layers=0
            )
            self.HAS_MODEL = True
        except Exception as e:
            self.HAS_MODEL = False
            print(f"Prompt generator disabled: {str(e)}")

    def generate(self) -> str:
        if not self.HAS_MODEL:
            return "Error: Prompt generator not available (missing Qwen2-0.5B)."
        prompt = """
        Generate a unique, complex prompt for testing an AI orchestration system.
        Requirements:
        1. Include 2-3 sequential steps (e.g., "First X, then Y").
        2. Mix creative and analytical tasks.
        3. Be realistic and human-like.
        4. Test both on-device and cloud capabilities.
        Example: "First, summarize this PDF about climate change. Then, write a tweet thread explaining the key points."
        """
        output = self.llm(
            prompt=prompt,
            max_tokens=150,
            temperature=0.9
        )["choices"][0]["text"].strip()
        return output

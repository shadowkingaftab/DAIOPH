from core.hybrid_orchestrator import HybridOrchestrator
try:
    orc = HybridOrchestrator(
        distilbert_path="distilbert-base-uncased",
        qwen_path="models/qwen2-0_5b-instruct-q4_k_m.gguf",
        grok_api_key=None
    )
    print("Orchestrator initialization successful.")
    print("HAS_QWEN:", orc.executor.HAS_QWEN)
except Exception as e:
    import traceback
    traceback.print_exc()

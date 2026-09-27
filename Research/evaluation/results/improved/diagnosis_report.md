# Benchmark Diagnosis

## Dataset integrity

- Prompt count: 60
- Unique prompt IDs: 60
- Duplicate IDs: 0
- Exact duplicate prompts: 0
- Classifier errors: 0

## Pre-registered distribution

| Field | Distribution |
|---|---|
| Categories | {'Complex and multi-step tasks': 20, 'Critical, urgent, and uncertain tasks': 20, 'Simple local tasks': 20} |
| Expected intents | {'ambiguous': 10, 'analyze_data': 5, 'generate_code': 5, 'multi_step': 10, 'simple_query': 6, 'summarize': 7, 'translate': 7, 'urgent': 10} |
| Expected routes | {'Cloud LLM': 30, 'Hybrid': 10, 'ODA': 20} |

## Interpretation limits

- This is a fixed, human-labeled internal benchmark. It supports a claim about these prompts and the recorded environment, not all user requests.
- Routing accuracy measures the decision route, not response correctness, helpfulness, or factuality.
- The benchmark runner does not execute cloud or local models. Output-quality, safety-red-team, and Liquid Neural Transformer adaptation claims require separate experiments.

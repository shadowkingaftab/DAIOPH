# Benchmark Diagnosis

## Dataset integrity

- Prompt count: 1
- Unique prompt IDs: 1
- Duplicate IDs: 0
- Exact duplicate prompts: 0
- Classifier errors: 0

## Pre-registered distribution

| Field | Distribution |
|---|---|
| Categories | {'Simple local tasks': 1} |
| Expected intents | {'translate': 1} |
| Expected routes | {'ODA': 1} |

## Interpretation limits

- This is a fixed, human-labeled internal benchmark. It supports a claim about these prompts and the recorded environment, not all user requests.
- Routing accuracy measures the decision route, not response correctness, helpfulness, or factuality.
- The benchmark runner does not execute cloud or local models. Output-quality, safety-red-team, and Liquid Neural Transformer adaptation claims require separate experiments.

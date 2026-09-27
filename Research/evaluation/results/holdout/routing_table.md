# DAIOPH Intent Routing Benchmark

- Run time (UTC): 2026-09-27T05:50:32.109641+00:00
- Classifier: `typeform/distilbert-base-uncased-mnli`
- Evaluation mode: local classifier and route decision only; no prompt execution.

## Table V. Intent Routing Accuracy by Prompt Category

| Category | Prompts | Correct | Accuracy |
|---|---:|---:|---:|
| Simple local tasks | 20 | 20 | 100.00% |
| Complex and multi-step tasks | 20 | 20 | 100.00% |
| Critical, urgent, and uncertain tasks | 20 | 19 | 95.00% |
| Overall | 60 | 59 | 98.33% |

## Supporting Metrics

- Intent accuracy: 98.33% (59/60)
- Mean classification latency: 1134.32 ms
- P95 classification latency: 1441.33 ms
- Local-eligible prompts kept local: 100.00%
- Risk-route compliance: 97.50%

`Risk-route compliance` measures whether prompts marked urgent, uncertain, or complex received their pre-registered expected route. It does not establish general system safety or output quality.

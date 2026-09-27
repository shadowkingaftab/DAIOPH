# DAIOPH Intent Routing Benchmark

- Run time (UTC): 2026-09-27T05:37:09.106752+00:00
- Classifier: `typeform/distilbert-base-uncased-mnli`
- Evaluation mode: local classifier and route decision only; no prompt execution.

## Table V. Intent Routing Accuracy by Prompt Category

| Category | Prompts | Correct | Accuracy |
|---|---:|---:|---:|
| Simple local tasks | 20 | 10 | 50.00% |
| Complex and multi-step tasks | 20 | 8 | 40.00% |
| Critical, urgent, and uncertain tasks | 20 | 14 | 70.00% |
| Overall | 60 | 32 | 53.33% |

## Supporting Metrics

- Intent accuracy: 38.33% (23/60)
- Mean classification latency: 1000.23 ms
- P95 classification latency: 1514.54 ms
- Local-eligible prompts kept local: 50.00%
- Risk-route compliance: 55.00%

`Risk-route compliance` measures whether prompts marked urgent, uncertain, or complex received their pre-registered expected route. It does not establish general system safety or output quality.

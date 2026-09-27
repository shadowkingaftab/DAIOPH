# DAIOPH Intent Routing Benchmark

- Run time (UTC): 2026-09-27T05:54:31.429472+00:00
- Classifier: `typeform/distilbert-base-uncased-mnli`
- Explicit routing signals enabled: False
- Evaluation mode: local classifier and route decision only; no prompt execution.

## Table V. Intent Routing Accuracy by Prompt Category

| Category | Prompts | Correct | Accuracy |
|---|---:|---:|---:|
| Simple local tasks | 20 | 11 | 55.00% |
| Complex and multi-step tasks | 20 | 5 | 25.00% |
| Critical, urgent, and uncertain tasks | 20 | 14 | 70.00% |
| Overall | 60 | 30 | 50.00% |

## Supporting Metrics

- Intent accuracy: 40.00% (24/60)
- Mean classification latency: 992.57 ms
- P95 classification latency: 1248.20 ms
- Local-eligible prompts kept local: 55.00%
- Risk-route compliance: 47.50%

`Risk-route compliance` measures whether prompts marked urgent, uncertain, or complex received their pre-registered expected route. It does not establish general system safety or output quality.

# DAIOPH Intent Routing Benchmark

- Run time (UTC): 2026-09-27T05:44:43.878827+00:00
- Classifier: `typeform/distilbert-base-uncased-mnli`
- Evaluation mode: local classifier and route decision only; no prompt execution.

## Table V. Intent Routing Accuracy by Prompt Category

| Category | Prompts | Correct | Accuracy |
|---|---:|---:|---:|
| Simple local tasks | 20 | 20 | 100.00% |
| Complex and multi-step tasks | 20 | 20 | 100.00% |
| Critical, urgent, and uncertain tasks | 20 | 20 | 100.00% |
| Overall | 60 | 60 | 100.00% |

## Supporting Metrics

- Intent accuracy: 100.00% (60/60)
- Mean classification latency: 552.72 ms
- P95 classification latency: 1064.91 ms
- Local-eligible prompts kept local: 100.00%
- Risk-route compliance: 100.00%

`Risk-route compliance` measures whether prompts marked urgent, uncertain, or complex received their pre-registered expected route. It does not establish general system safety or output quality.

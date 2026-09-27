# DAIOPH Intent Routing Benchmark

- Run time (UTC): 2026-09-27T05:34:19.716483+00:00
- Classifier: `typeform/distilbert-base-uncased-mnli`
- Evaluation mode: local classifier and route decision only; no prompt execution.

## Table V. Intent Routing Accuracy by Prompt Category

| Category | Prompts | Correct | Accuracy |
|---|---:|---:|---:|
| Simple local tasks | 1 | 0 | 0.00% |
| Overall | 1 | 0 | 0.00% |

## Supporting Metrics

- Intent accuracy: 100.00% (1/1)
- Mean classification latency: 6024.99 ms
- P95 classification latency: 6024.99 ms
- Local-eligible prompts kept local: 0.00%
- Risk-route compliance: 0.00%

`Risk-route compliance` measures whether prompts marked urgent, uncertain, or complex received their pre-registered expected route. It does not establish general system safety or output quality.

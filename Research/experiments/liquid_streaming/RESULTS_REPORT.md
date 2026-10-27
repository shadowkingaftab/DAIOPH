# Liquid Streaming Study: Validated Results

## Run and validation

The definitive corrected run is `20261027-025335`: 3 seeds, 5 chunks, 6 models, 270/270 cells completed, zero failures. Dataset SHA-256: `36923c3705a59e08fe9c3883d8bc2dd966ef93e22cb78ac41171782a698d56e0`.

Validation performed after the run:

- Every one of the 270 accuracy records exactly matches the corresponding grouped per-example predictions and correct-count totals.
- All 22 artifacts listed in the lock file match their recorded SHA-256 hashes and byte sizes.
- `failures.csv` contains its header only; `status.json` reports completed.
- Stable append-only class indices are covered by `test_class_mapping.py`.

Run report: `outputs/runs/20261027-025335/RUN_REPORT.md`. Exact command, environment, configuration, and data provenance are in `outputs/runs/20261027-025335/run_manifest.json`; the full lock is `outputs/locks/20261027-025335.json`.

## Observed final-step accuracy

Mean ± standard deviation across 3 seeds. Rows are evaluation chunks after training through chunk 4; chunk 4 is the newly arriving chunk.

| Model | Chunk 0 | Chunk 1 | Chunk 2 | Chunk 3 | New chunk 4 |
|---|---:|---:|---:|---:|---:|
| CfC (default) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0033 ± 0.0058 | 0.7774 ± 0.0316 |
| CfC (no gate) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0030 ± 0.0017 | 0.7600 ± 0.0366 |
| CfC (pure) | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.5970 ± 0.0061 |
| GRU | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0004 ± 0.0006 | 0.0385 ± 0.0084 | 0.8952 ± 0.0093 |
| LSTM | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0141 ± 0.0045 | 0.8819 ± 0.0124 |
| TF-IDF + SGD | 0.1352 ± 0.0023 | 0.4678 ± 0.0029 | 0.7159 ± 0.0006 | 0.8315 ± 0.0006 | 0.9207 ± 0.0006 |

The neural models learn the newest chunk, then have near-zero accuracy on most earlier chunks after sequential training without replay or regularization. CfC does not outperform the GRU, LSTM, or TF-IDF + SGD on the newest chunk. TF-IDF + SGD uses a fixed full-label output space; neural heads grow as classes arrive, so this is not a fully matched output-space comparison. Treat these as protocol-specific descriptive results, not evidence of general model superiority.

## Interpretation limits

- Three seeds are too few for strong inferential claims. Report means and spread descriptively; do not present the intervals as robust significance evidence.
- Calibration scores are computed over each model's own output space and are not directly comparable across different output spaces.
- Latency is single-example, end-to-end CPU latency including tokenization/vectorization; it does not establish production throughput.
- This standalone study does not demonstrate improvement to the wider DAIOPH engine.
- No replay, distillation, or continual-learning regularizer is used. Severe forgetting is the observed outcome under this protocol.

## Superseded artifacts

Run `20261024-225329` predates the stable append-only class-index correction. Growing the neural head could reorder old class labels while leaving existing head rows in place, invalidating old-class predictions. Do not use that run's metrics or figures as the study result. Its files remain as historical artifacts; corrected code and locked results are in run `20261027-025335`.

Run `20261024-203310` is incomplete and is not a result. Run `20261027-025256` was an aborted zero-cell attempt. `outputs/mapping_check/` is a focused diagnostic, not a full study run.

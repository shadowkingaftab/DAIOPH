# Paper Skeleton: Liquid Streaming (CfC) for Class-Incremental Intent Classification

## Title
Liquid Streaming: Closed-form Continuous-time Networks for Class-Incremental Intent Classification on CLINC150

## Abstract (placeholder)
**Pending.** To be filled using only actual saved results from `outputs/runs/20261024-225329/`. No speculative claims.

## Introduction (placeholder)
**Pending.** Frame class-incremental streaming (train on arriving chunk only, test on all seen). Cite CLINC150. State evaluation scope (150 intents, 5×30 chunks). Do not claim SOTA without evidence.

## Method

### Task stream construction (from saved manifests)
- Dataset: CLINC150 (in-scope only), source https://github.com/clinc/oos-eval (commit 828f809, 2021-06-01). File `clinc150_full.json` SHA256 `36923c3705a59e08fe9c3883d8bc2dd966ef93e22cb78ac41171782a698d56e0` (2,495,390 bytes).
- Splits: train 15000, val 3000, test 4500 (intent field = second element of [text,intent]).
- Chunking: deterministic chunk_seed=12345, 5 chunks × 30 intents (intent_order and chunk membership recorded in run_manifest.json). Protocol: sequential class-incremental streaming; train on arriving chunk only; test on all seen chunks.

### Models
- **CfC (ncps)**: `CfCTextClassifier` (Embedding→CfC→Linear). `ncps==1.0.1`. Modes: `default`, `pure`, `no_gate`. Neural heads grow with seen classes.
- **Baselines**: LSTM, GRU (growing heads). TF-IDF (fit on train text only) + SGDClassifier (log_loss, fixed full-label output space, updated via partial_fit per chunk) — documented baseline protocol.
- **Calibration**: Temperature scaling fitted on current-chunk validation logits/probs only (not test), applied to test; ECE/Brier reported per model's own output space.

### Training/eval details
- Seeds: 0,1,2. Batch 32, lr 1e-3, max_epochs 10, patience 2, max_len 64, embed/hidden 64. SGD 5 epochs/chunk, max_features 50000. Metrics/size/latency computed in-process.

## Experimental Protocol (from run manifest)
- Run: `20261024-225329` (seeds 0,1,2, num_chunks 5). Command/argv recorded. Environment (Python 3.13.9, torch 2.11.0, ncps 1.0.1, sklearn 1.8.0, pandas 2.2.3, numpy 2.3.5, matplotlib 3.9.2), CPU-only. Test used for evaluation only.
- Cells: 270/270 completed, 0 failures. Per-example 243000, learning curves 809, model metrics 18.

## Results

### Tables (use actual values; mark pending if not present)
**Table 1: Final accuracy (eval on all seen chunks, last chunk_step)** — *pending extraction from raw_results.csv/aggregates*
**Table 2: Accuracy matrix summary by chunk_step** — *pending* (see `outputs/aggregated/20261024-225329_run_matrix_summary.csv`)
**Table 3: Forgetting/retention** — *pending* (figure references below)
**Table 4: Calibration (ECE/Brier)** — *pending* (see raw_results.csv columns ece_calibrated/brier_calibrated)
**Table 5: Model size and latency (CPU, single-example)** — *pending* (see `model_metrics.csv`)

### Figure references (regenerated from saved CSVs)
- `outputs/figures/20261024-225329/accuracy_by_chunk_step.png`
- `outputs/figures/20261024-225329/accuracy_heatmap.png`
- `outputs/figures/20261024-225329/retention_by_model.png`
- `outputs/figures/20261024-225329/forgetting_after_each_chunk.png`
- `outputs/figures/20261024-225329/within_chunk_learning_curves.png`
- `outputs/figures/20261024-225329/model_size_latency.png`
- `outputs/figures/20261024-225329/calibration_reliability.png`
- `outputs/figures/20261024-225329/calibration_ece_brier.png`
- Plus 2 additional figures in `outputs/figures/20261024-225329/` (see figure_manifest.json)

All figures generated from saved CSVs only (figure_manifest.json).

## Limitations
- CPU-only, small model sizes (embed/hidden 64), limited epochs (10) with patience 2.
- Class-incremental with growing heads for neural nets; SGD fixed full space (documented difference).
- No persistent checkpoints saved by study pipeline.
- Calibration/metrics computed per model's own output space (caveat for cross-model ECE/Brier).
- Latency single-example CPU only.
- 3 seeds only; CI reported as t-interval.
- **Do not claim** end-to-end engine improvement from this standalone benchmark; adapter integration is separate and optional.

## Citations
- CLINC150: Larson et al., "An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction", EMNLP 2019 (and clinc/oos-eval repo). Repo: https://github.com/clinc/oos-eval
- CfC / Neural Circuit Policies: Hasani et al., "Liquid Time-constant Networks", AAAI 2021; Lechner et al. CfC. Implementation: ncps (https://github.com/mlech26l/ncps), version 1.0.1.
- Class-incremental learning baselines (general): Van de Ven & Tolias (2019), etc. — cite as appropriate; results here are protocol-specific, not a broad benchmark sweep.
- Calibration: Guo et al., "On Calibration of Modern Neural Networks", ICML 2017 (temperature scaling).

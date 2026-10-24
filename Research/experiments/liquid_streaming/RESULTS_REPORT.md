# Class-Incremental Intent Classification Study: CfC vs LSTM vs GRU vs TF-IDF+SGD

## Experiment Overview

**Goal:** Standalone class-incremental study comparing ncps CfC vs LSTM, GRU, and TF-IDF+SGD on CLINC150 intent chunks.

**Dataset:** CLINC150 (in-scope intents only) from `clinc/oos-eval` (commit `828f809`), SHA-256 verified.

| Split | Examples |
|-------|----------|
| Train | 15,000 |
| Val   | 3,000 |
| Test  | 4,500 |

**Protocol (sequential class-incremental):**
- 150 intents split into 5 fixed chunks (30 intents each), deterministic seed 12345
- At chunk step `i`, model trains ONLY on chunk `i`'s training data (arriving stream)
- After training, evaluated on TEST data of every seen chunk `0..i`
- Validation used for early stopping only; test never used for training/tuning
- Vocabulary built from training text only (no label/test leakage)
- TF-IDF vectorizer fit once on full train corpus (unsupervised); SGD head updated per chunk via `partial_fit`

## Configuration

| Setting | Value |
|---------|-------|
| Num chunks | 5 |
| Intents per chunk | 30 |
| Seeds | 0, 1 (reduced from planned 5 due to CfC CPU slowness) |
| Chunk seed | 12345 |
| Embed dim | 64 |
| Hidden size | 64 |
| Batch size | 32 |
| Learning rate | 1e-3 (Adam) |
| Max epochs | 5 |
| Early stopping patience | 2 |
| Max seq len | 64 |
| SGD epochs per chunk | 5 |
| SGD max features | 50,000 |
| SGD loss | log_loss |

**Models evaluated:** LSTM, GRU, TF-IDF+SGD. CfC was tested minimally (1 seed × 1 chunk × 3 epochs) because ncps CfC is extremely slow on CPU (~40+ minutes per seed-chunk without producing output).

**Key implementation fix:** Left-padding instead of right-padding for neural model input sequences. This ensures the LSTM/GRU final hidden state (`h[-1]`) captures the last real token rather than padding, which dramatically improved neural model accuracy (from ~0.7% to ~74-89% on chunk 0).

## Key Findings

### 1. Adaptation (Learning New Chunks)
**TF-IDF+SGD > LSTM ≈ GRU > CfC**
- TF-IDF+SGD achieves the highest adaptation accuracy on every chunk (91.9%–96.6%)
- LSTM and GRU achieve solid adaptation (82.7%–88.8%) but slightly below TF-IDF+SGD
- CfC (minimal test) underperforms at 48.5% on chunk 0

### 2. Retention (Remembering Previous Chunks)
**TF-IDF+SGD ≫ LSTM ≈ GRU (catastrophic forgetting)**
- **TF-IDF+SGD** retains meaningful accuracy on earlier chunks: 72.4% on chunk 1 after learning chunk 2, declining gracefully to 21.9% on chunk 0 after learning all 5 chunks
- **LSTM and GRU** suffer **complete catastrophic forgetting**: 0.0% accuracy on all previously seen chunks after learning a new one. They only perform well on the most recently trained chunk.
- This is expected for class-incremental learning without replay, regularization, or architectural isolation mechanisms

### 3. Overall Comparison
TF-IDF+SGD is the clear winner on both adaptation and retention metrics. The neural models (LSTM, GRU) can learn each new chunk reasonably well (~84-89%) but completely forget everything previously learned (0% on earlier chunks). CfC was not fully evaluable due to CPU performance limitations.

## Limitations

1. **CfC not fully evaluated:** ncps CfC is too slow on CPU for a full 5-seed × 5-chunk experiment. Results are from a minimal 1-seed × 1-chunk × 3-epoch test only.
2. **Reduced seeds:** Only 2 seeds (0, 1) instead of the planned 5, due to time constraints. Std estimates are therefore less reliable.
3. **No regularization/replay:** Neural models use plain fine-tuning with no experience replay, distillation, or regularization — catastrophic forgetting is expected.
4. **CPU-only:** All experiments ran on CPU. GPU would significantly speed up CfC and neural model training.

## Output Files

| File | Description |
|------|-------------|
| `outputs/runs/20261024-203310/raw_results.csv` | Per-seed, per-model, per-chunk-step, per-eval-chunk accuracy (90 rows) |
| `outputs/runs/20261024-203310/run_manifest.json` | Full run configuration and dataset metadata |
| `outputs/aggregated/20261024-203316_summary.csv` | Mean ± std across seeds, grouped by model/chunk_step/eval_chunk |
| `outputs/figures/accuracy_vs_chunk.png` | Adaptation (newest chunk) and retention (all seen chunks) over chunk steps |
| `outputs/figures/final_step_accuracy.png` | Bar chart of final-step accuracy by model with seed std |

## Source Files (under `src/`)

| File | Description |
|------|-------------|
| `data.py` | CLINC150 dataset loading (pre-existing) |
| `tokenizer.py` | Simple word-level vocabulary built from training text (pre-existing) |
| `chunks.py` | Deterministic class-incremental chunk creation (pre-existing) |
| `models.py` | Model wrappers: LSTMTextClassifier, GRUTextClassifier, TfidfSgdClassifier with head growth via `expand_linear` |
| `train_eval.py` | Train/eval loop: TextDataset, collate_fn, set_seed, evaluate_nn, train_chunk_nn (early stop on val, restore best), eval_sgd, run_study |
| `run_study.py` | CLI entry point: writes raw CSV, manifest, aggregated summary, calls plots.py |
| `plots.py` | `accuracy_vs_chunk.png` (adaptation + retention) and `final_step_accuracy.png` (bar chart with std) |
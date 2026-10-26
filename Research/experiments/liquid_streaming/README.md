# Liquid Streaming Study

This package contains the class-incremental streaming experiment for CfC (Closed-form Continuous-time) and baselines (LSTM, GRU, TF-IDF+SGD) on CLINC150.

## Scope
- **Package root**: `Research/experiments/liquid_streaming/`
- **Task**: Sequential class-incremental intent classification (arrive 1 chunk at a time, train on arriving chunk only, test on all seen chunks)
- **Data**: CLINC150 (in-scope intents only; oos splits unused). 5 deterministic chunks × 30 intents (chunk_seed=12345), 150 total intents
- **Splits**: train 15000, val 3000, test 4500 (from dataset_manifest.json)
- **Checksum**: clinc150_full.json SHA256 `36923c3705a59e08fe9c3883d8bc2dd966ef93e22cb78ac41171782a698d56e0`, 2,495,390 bytes (verified in run manifest)
- **CfC API/version**: `ncps==1.0.1` (PyPI wheel). API usage: `CfC(input_size=..., units=..., return_sequences=False, batch_first=True, mixed_memory=..., mode=...)` via `ncps.torch`. Modes: `default`, `pure`, `no_gate`.
- **Models**: `cfc` (default), `cfc_ablation_pure`, `cfc_ablation_no_gate`, `lstm`, `gru`, `tfidf_sgd`. Neural heads grow with seen classes (class-incremental). TF-IDF+SGD uses fixed full-label output space (documented baseline).
- **Seeds**: 0,1,2 (3 seeds). CI: 95% t-interval across seeds (df=n-1).
- **Update budgets**: Train on arriving chunk only per step (class-incremental). Neural: batch_size=32, lr=0.001, max_epochs=10, patience=2, embed_dim=64, hidden_size=64, max_len=64. SGD: 5 epochs per chunk, max_features=50000.
- **Metrics**: Accuracy per (model,seed,chunk_step,eval_chunk); learning curves (train/val loss/acc per epoch within chunk); calibration (ECE/Brier, temperature scaling fitted on current-chunk val only); model size (serialized params/bytes), single-example end-to-end CPU latency (p50/p95/mean) incl. tokenization/vectorization, batch_size=1.
- **Hardware (completed run 20261024-225329)**: Windows-11-10.0.26200, Intel64 Family 6 Model 186 Stepping 2 (12 cores), Python 3.13.9, no CUDA, torch threads 8. See `outputs/runs/20261024-225329/run_manifest.json` for full env.
- **Known limitations**: No persistent model checkpoints written by study (metrics/size/latency measured in-process); CfC API availability depends on ncps==1.0.1; CPU-only; t-CI requires ≥2 seeds; ECE/Brier computed per model's own output space (SGD full 150-class); latency is single-example CPU only; no claim of CfC superiority.

## Exact reproducibility commands (PowerShell)

**1) Recreate environment (project-local venv only)**
```powershell
# From Research/experiments/liquid_streaming/
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
If execution policy blocks: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**2) Regenerate figures/aggregates from saved results (no training)**
```powershell
# From Research/experiments/liquid_streaming/
.\.venv\Scripts\Activate.ps1
python src/plot_results.py --run-id 20261024-225329
# Or regenerate all aggregates/figures from outputs/runs/*
python -m src.preflight  # optional validation
```
Figures are generated from saved CSVs only (see `outputs/figures/20261024-225329/figure_manifest.json`).

**3) Rerun training (separate command)**
```powershell
# From Research/experiments/liquid_streaming/
.\.venv\Scripts\Activate.ps1
python src/run_study.py --seeds 0,1,2 --num-chunks 5 --max-epochs 10 --patience 2 --batch-size 32 --calibrate --latency-examples 100 --latency-warmup 5
```
Smokes: `python smoke.py`, `python smoke_train_eval.py`, `python smoke_day4.py`. Test: `python cfc_test.py`.

## Result files (saved)
- Run: `outputs/runs/20261024-225329/` (raw_results.csv, per_example_predictions.csv, learning_curves.csv, model_metrics.csv, failures.csv, run_manifest.json, RUN_REPORT.md, status.json)
- Aggregates: `outputs/aggregated/` (20261024-225329_*, run_matrix*, summaries)
- Figures: `outputs/figures/20261024-225329/` (10 PNGs + figure_manifest.json)
- Other runs present: `outputs/runs/20261024-203310/` (raw_results.csv, run_manifest.json only - incomplete)

## Traceability
- All reported metrics in `outputs/aggregated/*` trace to `outputs/runs/*/raw_results.csv` rows (protocol in run_manifest).
- Figures generated from saved CSVs only (confirmed by `figure_manifest.json` note).
- Dataset integrity verified (SHA256/size match in run_manifest).

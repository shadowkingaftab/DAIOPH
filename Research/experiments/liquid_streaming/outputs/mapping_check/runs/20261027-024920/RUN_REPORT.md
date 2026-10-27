# Run 20261027-024920 - liquid streaming study

This report is generated automatically from the locked run artefacts.
It reports observed results only; it does not claim that any model wins.

## Provenance

- Command: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\.venv\Scripts\python.exe src\run_study.py --seeds 0 --num-chunks 5 --models cfc --out outputs\mapping_check --no-per-example --no-calibrate --max-epochs 4 --patience 2 --latency-examples 10 --latency-warmup 1`
- Started (UTC): 2026-10-26T21:19:20.217340+00:00
- Finished (UTC): 2026-10-26T21:22:07.622026+00:00
- Elapsed seconds: 167.405
- Git HEAD: `7f566faacc6daf42efa640a489282ca894cdc0c4`
- Git status (porcelain): `M Research/experiments/liquid_streaming/src/train_eval.py; ?? Research/experiments/liquid_streaming/outputs/mapping_check/`
- Dataset: CLINC150
- Dataset SHA-256: `36923c3705a59e08fe9c3883d8bc2dd966ef93e22cb78ac41171782a698d56e0`
- Dataset integrity OK: True
- Python: 3.13.9 | packaged by Anaconda, Inc. | (main, Oct 21 2025, 19:09:58) [MSC v.1929 64 bit (AMD64)]
- Packages: {"numpy": "2.3.5", "pandas": "2.2.3", "scipy": "1.17.1", "scikit-learn": "1.8.0", "torch": "2.11.0", "ncps": "1.0.1", "matplotlib": "3.9.2"}
- Seeds: [0]
- Chunks: 5
- Models: ['cfc']
- Calibration: temperature scaling fitted on current-chunk validation logits/log-probabilities; applied to test probabilities
- CI method: 95% two-sided t CI across seeds: mean +/- t(0.975, df=n-1)*std/sqrt(n); requires >=2 seeds

## Run matrix

- Expected cells: 15
- Completed cells: 15
- Missing cells: 0
- Status: **completed**
- Matrix: `outputs\mapping_check\aggregated\20261027-024920_run_matrix.csv`
- Matrix summary: `outputs\mapping_check\aggregated\20261027-024920_run_matrix_summary.csv`

## Final-step aggregate (mean +/- std over seeds)

```
model  chunk_step  eval_chunk  accuracy_mean  accuracy_std  accuracy_ci95_low  accuracy_ci95_high  ece_calibrated_mean  brier_calibrated_mean
  cfc           4           0            NaN           NaN                NaN                 NaN                  NaN                    NaN
  cfc           4           1            NaN           NaN                NaN                 NaN                  NaN                    NaN
  cfc           4           2            NaN           NaN                NaN                 NaN                  NaN                    NaN
  cfc           4           3            NaN           NaN                NaN                 NaN                  NaN                    NaN
  cfc           4           4            NaN           NaN                NaN                 NaN                  NaN                    NaN
```

## Figures (regenerated from saved CSVs only)

- Figure directory: `outputs\mapping_check\figures\20261027-024920`
- `adaptation_current_chunk.png`
- `adaptation_mean_seen_chunks.png`
- `retention_by_model.png`
- `forgetting_after_each_chunk.png`
- `model_size_latency.png`
- `calibration_ece_brier.png`
- `within_chunk_learning_curves.png`

Reproduce figures without training:

```powershell
.venv\Scripts\python.exe src\plot_results.py --run-dir "outputs\mapping_check\runs\20261027-024920" --out "outputs\mapping_check\figures\20261027-024920"
```

## Artefacts

- summary: `outputs\mapping_check\aggregated\20261027-024920_summary.csv`
- model_metrics_summary: `outputs\mapping_check\aggregated\20261027-024920_model_metrics_summary.csv`
- run_matrix: `outputs\mapping_check\aggregated\20261027-024920_run_matrix.csv`
- run_matrix_summary: `outputs\mapping_check\aggregated\20261027-024920_run_matrix_summary.csv`
- run_matrix_overall: `outputs\mapping_check\aggregated\20261027-024920_run_matrix_overall.json`
- figure_manifest: `outputs\mapping_check\figures\20261027-024920\figure_manifest.json`
- lock: `outputs\mapping_check\locks\20261027-024920.json`

## Caveats

- Neural heads grow with seen classes; TF-IDF+SGD uses a fixed full-label output space.
- ECE/Brier are computed over each model's own output space.
- Latency is single-example end-to-end CPU latency including tokenization/vectorization.
- No replay, distillation or regularization is used; forgetting is expected in this protocol.
- Figures are descriptive; no significance claim is made from three seeds.

Lock file: `outputs\mapping_check\locks\20261027-024920.json`
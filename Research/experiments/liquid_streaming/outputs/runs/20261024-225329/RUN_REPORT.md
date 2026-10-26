# Run 20261024-225329 - liquid streaming study

This report is generated automatically from the locked run artefacts.
It reports observed results only; it does not claim that any model wins.

## Provenance

- Command: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\.venv\Scripts\python.exe src\run_study.py --seeds 0,1,2 --num-chunks 5 --max-epochs 10 --patience 2 --batch-size 32 --calibrate --latency-examples 100 --latency-warmup 5`
- Started (UTC): 2026-10-24T17:23:29.125043+00:00
- Finished (UTC): 2026-10-24T18:12:06.605953+00:00
- Elapsed seconds: 2917.481
- Git HEAD: `113818036b6c2f5c3138c48551fef8b90ff9511f`
- Git status (porcelain): `M Research/experiments/liquid_streaming/out_day2_smoke/predictions.csv;  M Research/experiments/liquid_streaming/out_day2_smoke/raw_results.csv;  M Research/experiments/liquid_streaming/out_day2_smoke/run_metadata.json;  M Research/experiments/liquid_streaming/src/models.py;  M Research/experiments/liquid_streaming/src/run_study.py;  M Research/experiments/liquid_streaming/src/train_eval.py; ?? Research/experiments/liquid_streaming/out_day4_smoke/; ?? Research/experiments/liquid_streaming/out_train_eval_smoke/; ?? Research/experiments/liquid_streaming/outputs/preflight.json; ?? Research/experiments/liquid_streaming/outputs/runs/20261024-225329/; ?? Research/experiments/liquid_streaming/smoke_day4.py; ?? Research/experiments/liquid_streaming/smoke_train_eval.py; ?? Research/experiments/liquid_streaming/src/calibration.py; ?? Research/experiments/liquid_streaming/src/day4_runner.py; ?? Research/experiments/liquid_streaming/src/plot_results.py; ?? Research/experiments/liquid_streaming/src/preflight.py; ?? Research/experiments/liquid_streaming/src/study_utils.py; ?? out_day3_smoke_report/; ?? out_smoke_test/`
- Dataset: CLINC150
- Dataset SHA-256: `36923c3705a59e08fe9c3883d8bc2dd966ef93e22cb78ac41171782a698d56e0`
- Dataset integrity OK: True
- Python: 3.13.9 | packaged by Anaconda, Inc. | (main, Oct 21 2025, 19:09:58) [MSC v.1929 64 bit (AMD64)]
- Packages: {"numpy": "2.3.5", "pandas": "2.2.3", "scipy": "1.17.1", "scikit-learn": "1.8.0", "torch": "2.11.0", "ncps": "1.0.1", "matplotlib": "3.9.2"}
- Seeds: [0, 1, 2]
- Chunks: 5
- Models: ['cfc', 'cfc_ablation_pure', 'cfc_ablation_no_gate', 'lstm', 'gru', 'tfidf_sgd']
- Calibration: temperature scaling fitted on current-chunk validation logits/log-probabilities; applied to test probabilities
- CI method: 95% two-sided t CI across seeds: mean +/- t(0.975, df=n-1)*std/sqrt(n); requires >=2 seeds

## Run matrix

- Expected cells: 270
- Completed cells: 270
- Missing cells: 0
- Status: **completed**
- Matrix: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261024-225329_run_matrix.csv`
- Matrix summary: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261024-225329_run_matrix_summary.csv`

## Final-step aggregate (mean +/- std over seeds)

```
               model  chunk_step  eval_chunk  accuracy_mean  accuracy_std  accuracy_ci95_low  accuracy_ci95_high  ece_calibrated_mean  brier_calibrated_mean
                 cfc           4           0         0.0000        0.0000             0.0000              0.0000               0.4806                 1.3337
                 cfc           4           1         0.0000        0.0000             0.0000              0.0000               0.4839                 1.3394
                 cfc           4           2         0.0000        0.0000             0.0000              0.0000               0.4820                 1.3349
                 cfc           4           3         0.0019        0.0032            -0.0061              0.0098               0.4957                 1.3474
                 cfc           4           4         0.7759        0.0239             0.7166              0.8353               0.0452                 0.3146
cfc_ablation_no_gate           4           0         0.0000        0.0000             0.0000              0.0000               0.4498                 1.3036
cfc_ablation_no_gate           4           1         0.0000        0.0000             0.0000              0.0000               0.4319                 1.2839
cfc_ablation_no_gate           4           2         0.0000        0.0000             0.0000              0.0000               0.4423                 1.2970
cfc_ablation_no_gate           4           3         0.0030        0.0023            -0.0028              0.0087               0.4458                 1.2947
cfc_ablation_no_gate           4           4         0.7248        0.0256             0.6611              0.7885               0.0552                 0.3782
   cfc_ablation_pure           4           0         0.0000        0.0000             0.0000              0.0000               0.3017                 1.1803
   cfc_ablation_pure           4           1         0.0000        0.0000             0.0000              0.0000               0.3024                 1.1872
   cfc_ablation_pure           4           2         0.0000        0.0000             0.0000              0.0000               0.2835                 1.1656
   cfc_ablation_pure           4           3         0.0000        0.0000             0.0000              0.0000               0.3003                 1.1785
   cfc_ablation_pure           4           4         0.6056        0.0048             0.5935              0.6176               0.1072                 0.5461
                 gru           4           0         0.0000        0.0000             0.0000              0.0000               0.5350                 1.3909
                 gru           4           1         0.0000        0.0000             0.0000              0.0000               0.5200                 1.3774
                 gru           4           2         0.0004        0.0006            -0.0012              0.0020               0.5457                 1.4070
                 gru           4           3         0.0007        0.0006            -0.0009              0.0023               0.5459                 1.4049
                 gru           4           4         0.8696        0.0078             0.8502              0.8890               0.0310                 0.1824
                lstm           4           0         0.0000        0.0000             0.0000              0.0000               0.5455                 1.4050
                lstm           4           1         0.0000        0.0000             0.0000              0.0000               0.5239                 1.3807
                lstm           4           2         0.0000        0.0000             0.0000              0.0000               0.5502                 1.4119
                lstm           4           3         0.0011        0.0011            -0.0016              0.0039               0.5530                 1.4122
                lstm           4           4         0.8811        0.0087             0.8596              0.9027               0.0255                 0.1703
           tfidf_sgd           4           0         0.1352        0.0023             0.1294              0.1409               0.3722                 1.1732
           tfidf_sgd           4           1         0.4678        0.0029             0.4605              0.4751               0.2358                 0.8097
           tfidf_sgd           4           2         0.7159        0.0006             0.7143              0.7175               0.1107                 0.4176
           tfidf_sgd           4           3         0.8315        0.0006             0.8299              0.8331               0.0570                 0.2479
           tfidf_sgd           4           4         0.9207        0.0006             0.9191              0.9223               0.0355                 0.1292
```

## Figures (regenerated from saved CSVs only)

- Figure directory: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\figures\20261024-225329`
- `adaptation_current_chunk.png`
- `adaptation_mean_seen_chunks.png`
- `retention_by_model.png`
- `forgetting_after_each_chunk.png`
- `model_size_latency.png`
- `calibration_reliability.png`
- `calibration_ece_brier.png`
- `within_chunk_learning_curves.png`

Reproduce figures without training:

```powershell
.venv\Scripts\python.exe src\plot_results.py --run-dir "C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\runs\20261024-225329" --out "C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\figures\20261024-225329"
```

## Artefacts

- summary: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261024-225329_summary.csv`
- model_metrics_summary: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261024-225329_model_metrics_summary.csv`
- run_matrix: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261024-225329_run_matrix.csv`
- run_matrix_summary: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261024-225329_run_matrix_summary.csv`
- run_matrix_overall: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261024-225329_run_matrix_overall.json`
- figure_manifest: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\figures\20261024-225329\figure_manifest.json`
- lock: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\locks\20261024-225329.json`

## Caveats

- Neural heads grow with seen classes; TF-IDF+SGD uses a fixed full-label output space.
- ECE/Brier are computed over each model's own output space.
- Latency is single-example end-to-end CPU latency including tokenization/vectorization.
- No replay, distillation or regularization is used; forgetting is expected in this protocol.
- Figures are descriptive; no significance claim is made from three seeds.

Lock file: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\locks\20261024-225329.json`
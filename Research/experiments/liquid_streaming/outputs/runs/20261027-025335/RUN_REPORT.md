# Run 20261027-025335 - liquid streaming study

This report is generated automatically from the locked run artefacts.
It reports observed results only; it does not claim that any model wins.

## Provenance

- Command: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\.venv\Scripts\python.exe src\run_study.py --seeds 0,1,2 --num-chunks 5 --max-epochs 10 --patience 2 --batch-size 32 --calibrate --latency-examples 100 --latency-warmup 5`
- Started (UTC): 2026-10-26T21:23:35.249878+00:00
- Finished (UTC): 2026-10-26T22:32:28.744552+00:00
- Elapsed seconds: 4133.495
- Git HEAD: `7f566faacc6daf42efa640a489282ca894cdc0c4`
- Git status (porcelain): `M Research/experiments/liquid_streaming/src/train_eval.py; ?? Research/experiments/liquid_streaming/outputs/mapping_check/; ?? Research/experiments/liquid_streaming/outputs/runs/20261027-025256/; ?? Research/experiments/liquid_streaming/outputs/runs/20261027-025335/; ?? Research/experiments/liquid_streaming/src/class_mapping.py; ?? Research/experiments/liquid_streaming/test_class_mapping.py`
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
- Matrix: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261027-025335_run_matrix.csv`
- Matrix summary: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261027-025335_run_matrix_summary.csv`

## Final-step aggregate (mean +/- std over seeds)

```
               model  chunk_step  eval_chunk  accuracy_mean  accuracy_std  accuracy_ci95_low  accuracy_ci95_high  ece_calibrated_mean  brier_calibrated_mean
                 cfc           4           0         0.0000        0.0000             0.0000              0.0000               0.4784                 1.3318
                 cfc           4           1         0.0000        0.0000             0.0000              0.0000               0.4724                 1.3251
                 cfc           4           2         0.0000        0.0000             0.0000              0.0000               0.4687                 1.3223
                 cfc           4           3         0.0033        0.0058            -0.0110              0.0177               0.4825                 1.3297
                 cfc           4           4         0.7774        0.0316             0.6989              0.8559               0.0411                 0.3077
cfc_ablation_no_gate           4           0         0.0000        0.0000             0.0000              0.0000               0.4992                 1.3534
cfc_ablation_no_gate           4           1         0.0000        0.0000             0.0000              0.0000               0.4762                 1.3275
cfc_ablation_no_gate           4           2         0.0000        0.0000             0.0000              0.0000               0.4806                 1.3348
cfc_ablation_no_gate           4           3         0.0030        0.0017            -0.0013              0.0072               0.4962                 1.3404
cfc_ablation_no_gate           4           4         0.7600        0.0366             0.6692              0.8508               0.0429                 0.3303
   cfc_ablation_pure           4           0         0.0000        0.0000             0.0000              0.0000               0.2986                 1.1829
   cfc_ablation_pure           4           1         0.0000        0.0000             0.0000              0.0000               0.2759                 1.1648
   cfc_ablation_pure           4           2         0.0000        0.0000             0.0000              0.0000               0.2811                 1.1702
   cfc_ablation_pure           4           3         0.0000        0.0000             0.0000              0.0000               0.2920                 1.1705
   cfc_ablation_pure           4           4         0.5970        0.0061             0.5818              0.6122               0.1005                 0.5288
                 gru           4           0         0.0000        0.0000             0.0000              0.0000               0.5310                 1.3929
                 gru           4           1         0.0000        0.0000             0.0000              0.0000               0.5214                 1.3793
                 gru           4           2         0.0004        0.0006            -0.0012              0.0020               0.5337                 1.3920
                 gru           4           3         0.0385        0.0084             0.0176              0.0594               0.5109                 1.3363
                 gru           4           4         0.8952        0.0093             0.8720              0.9183               0.0238                 0.1527
                lstm           4           0         0.0000        0.0000             0.0000              0.0000               0.5715                 1.4343
                lstm           4           1         0.0000        0.0000             0.0000              0.0000               0.5545                 1.4154
                lstm           4           2         0.0000        0.0000             0.0000              0.0000               0.5722                 1.4374
                lstm           4           3         0.0141        0.0045             0.0029              0.0252               0.5687                 1.4083
                lstm           4           4         0.8819        0.0124             0.8511              0.9126               0.0239                 0.1697
           tfidf_sgd           4           0         0.1352        0.0023             0.1294              0.1409               0.3722                 1.1732
           tfidf_sgd           4           1         0.4678        0.0029             0.4605              0.4751               0.2358                 0.8097
           tfidf_sgd           4           2         0.7159        0.0006             0.7143              0.7175               0.1107                 0.4176
           tfidf_sgd           4           3         0.8315        0.0006             0.8299              0.8331               0.0570                 0.2479
           tfidf_sgd           4           4         0.9207        0.0006             0.9191              0.9223               0.0355                 0.1292
```

## Figures (regenerated from saved CSVs only)

- Figure directory: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\figures\20261027-025335`
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
.venv\Scripts\python.exe src\plot_results.py --run-dir "C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\runs\20261027-025335" --out "C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\figures\20261027-025335"
```

## Artefacts

- summary: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261027-025335_summary.csv`
- model_metrics_summary: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261027-025335_model_metrics_summary.csv`
- run_matrix: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261027-025335_run_matrix.csv`
- run_matrix_summary: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261027-025335_run_matrix_summary.csv`
- run_matrix_overall: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\aggregated\20261027-025335_run_matrix_overall.json`
- figure_manifest: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\figures\20261027-025335\figure_manifest.json`
- lock: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\locks\20261027-025335.json`

## Caveats

- Neural heads grow with seen classes; TF-IDF+SGD uses a fixed full-label output space.
- ECE/Brier are computed over each model's own output space.
- Latency is single-example end-to-end CPU latency including tokenization/vectorization.
- No replay, distillation or regularization is used; forgetting is expected in this protocol.
- Figures are descriptive; no significance claim is made from three seeds.

Lock file: `C:\Users\AFTAB AHMAD SAYED\Downloads\DAIOPH-main\DAIOPH-main\Research\experiments\liquid_streaming\outputs\locks\20261027-025335.json`
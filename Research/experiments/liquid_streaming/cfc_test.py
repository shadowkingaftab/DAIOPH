import sys
sys.path.insert(0, 'C:/Users/AFTAB AHMAD SAYED/Downloads/DAIOPH-main/DAIOPH-main/Research/experiments/liquid_streaming/src')
from pathlib import Path
from train_eval import run_study
import tempfile

# CfC only: 1 seed, 1 chunk, 3 epochs (minimal due to CPU slowness)
rd = Path(tempfile.mkdtemp())
rows, m = run_study(
    Path('C:/Users/AFTAB AHMAD SAYED/Downloads/DAIOPH-main/DAIOPH-main/Research/experiments/liquid_streaming/data'),
    rd, seeds=(0,), num_chunks=1, chunk_seed=12345, max_epochs=3, patience=2, max_len=64)
print('ROWS:', len(rows))
for r in rows:
    print(r['model'], r['chunk_step'], r['eval_chunk'], round(r['accuracy'], 4))
print('CFC TEST PASSED')
# Liquid Streaming - Day 1 Foundation

This is the Day 1 foundation under Research/experiments/liquid_streaming/.

## Environment setup (PowerShell, project-local venv only)

From the experiment directory:

`powershell
# Create project-local virtual environment
py -m venv .venv  # or python -m venv .venv if py launcher not available

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Upgrade pip/setuptools/wheel
python -m pip install --upgrade pip setuptools wheel

# Install study dependencies (only this requirements file)
pip install -r requirements.txt
`

If PowerShell blocks script execution, use:
`powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
`

## Run smoke check

`powershell
# From Research/experiments/liquid_streaming/
python smoke.py
`

The smoke command downloads/loads data (CLINC150 preferred, Banking77 fallback), creates five deterministic class-incremental chunks (persisting intent order and split metadata), builds a tokenizer from training text only, trains a CfC-based classifier (token embeddings -> CfC -> intent head) for one small chunk/one short pass, evaluates it, and writes outputs under out_smoke/ (result_row.json, run_metadata.json, chunks_meta.json, tokenizer.pkl).

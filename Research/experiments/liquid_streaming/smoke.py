import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "src"))
from src.train_smoke import run_smoke

if __name__ == '__main__':
    res = run_smoke()
    print(res)

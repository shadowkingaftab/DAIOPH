"""Download CLINC150 data_full.json from its documented source and record metadata."""
import json, hashlib, sys
from pathlib import Path
import requests

OUT = Path(__file__).resolve().parent / "clinc150_data_full.json"
URL = "https://raw.githubusercontent.com/clinc/oos-eval/master/data/data_full.json"
REPO_COMMIT_API = "https://api.github.com/repos/clinc/oos-eval/commits/master"

def main():
    r = requests.get(URL, timeout=180)
    print("HTTP", r.status_code, "bytes", len(r.content))
    r.raise_for_status()
    content = r.content
    OUT.write_bytes(content)
    print("sha256:", hashlib.sha256(content).hexdigest())
    d = json.loads(content.decode("utf-8"))
    print("TOP-LEVEL KEYS:", list(d.keys()))
    print("split sizes:", {k: len(v) for k, v in d.items()})
    # label counts over train
    for split in ("train", "val", "test"):
        if split in d:
            labels = [lab for _, lab in d[split]]
            from collections import Counter
            c = Counter(labels)
            print(split, "unique labels:", len(c), "total:", sum(c.values()))
            print("  label order (first 20):", sorted(c)[:20])
    # sample records
    for split in ("train", "val", "test"):
        if split in d and len(d[split]):
            print(split, "sample:", d[split][0])

if __name__ == "__main__":
    main()

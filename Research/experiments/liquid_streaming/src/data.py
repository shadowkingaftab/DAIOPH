from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import requests


CLINC150_URLS = [
    "https://raw.githubusercontent.com/clinc/oos-eval/master/data/data_full.json",
]
BANKING77_URL = "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/train.csv"


def _load_clinc150(data_dir: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    cache = data_dir / "clinc150_full.json"
    if cache.exists():
        with cache.open("r", encoding="utf-8") as f:
            return json.load(f)
    last_err = None
    for url in CLINC150_URLS:
        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            with cache.open("w", encoding="utf-8") as f:
                json.dump(data, f)
            return data
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Failed to download CLINC150: {last_err}")


def _load_banking77(data_dir: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    cache = data_dir / "banking77_train.csv"
    if cache.exists():
        with cache.open("r", encoding="utf-8") as f:
            content = f.read()
        return content
    try:
        resp = requests.get(BANKING77_URL, timeout=60)
        resp.raise_for_status()
        content = resp.text
        with cache.open("w", encoding="utf-8") as f:
            f.write(content)
        return content
    except Exception as e:
        raise RuntimeError(f"Failed to download Banking77: {e}")

def load_intent_dataset(data_dir: Path):
    """Try CLINC150 first (official splits), else Banking77 fallback."""
    try:
        data = _load_clinc150(data_dir)
        # CLINC150 format
        train = data.get("train", [])
        val = data.get("val", []) or data.get("valid", [])
        test = data.get("test", [])
        # Build list of (text, label)
        out_train = []
        out_val = []
        out_test = []
        for item in train:
            if isinstance(item, dict):
                out_train.append((item["text"], item["intent"]))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                out_train.append((item[0], item[1]))
        for item in val:
            if isinstance(item, dict):
                out_val.append((item["text"], item["intent"]))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                out_val.append((item[0], item[1]))
        for item in test:
            if isinstance(item, dict):
                out_test.append((item["text"], item["intent"]))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                out_test.append((item[0], item[1]))
        return {
            "name": "CLINC150",
            "train": out_train,
            "val": out_val,
            "test": out_test,
        }
    except Exception:
        pass
    # fallback Banking77
    try:
        content = _load_banking77(data_dir)
        lines = content.strip().splitlines()
        rows = []
        for l in lines[1:]:  # skip header
            # text,label
            if "," in l:
                parts = l.split(",")
                label = parts[-1].strip()
                text = ",".join(parts[:-1]).strip().strip('"')
                rows.append((text, label))
        # simple split
        n = len(rows)
        train = rows[: int(0.8 * n)]
        val = rows[int(0.8 * n): int(0.9 * n)]
        test = rows[int(0.9 * n):]
        return {
            "name": "Banking77",
            "train": train,
            "val": val,
            "test": test,
        }
    except Exception as e:
        raise RuntimeError(f"No dataset available: {e}")

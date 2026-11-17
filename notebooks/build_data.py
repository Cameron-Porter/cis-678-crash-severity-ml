"""Run from notebooks/: python build_data.py (python3 on macOS)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.preprocess import build_datasets, notebook_root


if __name__ == "__main__":
    splits = build_datasets(notebook_root())
    for name, frame in splits.items():
        print(f"{name}: {len(frame):,} crashes, {len(frame.columns)} columns; integrity checks passed")

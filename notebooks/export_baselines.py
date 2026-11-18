import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.preprocess import notebook_root
from src.evaluation.export_baselines import collect_handoff, save_handoff


if __name__ == '__main__':
    root = notebook_root()
    handoff = collect_handoff(root)
    print(handoff['metrics'].to_string(index=False))
    print('Handoff:', save_handoff(root, handoff))

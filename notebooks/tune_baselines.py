import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.preprocess import notebook_root
from src.models.data import load_baseline_inputs
from src.models.tune_baselines import tune_baselines, save_tuning_results


if __name__ == '__main__':
    root = notebook_root()
    inputs = load_baseline_inputs(root)
    tuning = tune_baselines(inputs)
    save_tuning_results(root, inputs, tuning)
    print(tuning['comparison'].to_string(index=False))
    print('Selected:', tuning['winner'])

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.preprocess import notebook_root
from src.models.data import load_baseline_inputs
from src.models.majority_baseline import fit_baselines, evaluate_baselines, save_baseline_results


if __name__ == '__main__':
    root = notebook_root()
    inputs = load_baseline_inputs(root)
    models = fit_baselines(inputs)
    results = evaluate_baselines(inputs, models)
    save_baseline_results(root, inputs, results)
    for configuration, result in results.items():
        print(configuration, result['metrics'])

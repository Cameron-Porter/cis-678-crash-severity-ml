import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.preprocess import notebook_root
from src.models.data import load_baseline_inputs
from src.models.logistic_regression import fit_logistic_models, evaluate_logistic_models, save_logistic_results


if __name__ == '__main__':
    root = notebook_root()
    inputs = load_baseline_inputs(root)
    models = fit_logistic_models(inputs)
    results = evaluate_logistic_models(inputs, models)
    save_logistic_results(root, inputs, models, results)
    for configuration, result in results.items():
        print(configuration, result['metrics'])

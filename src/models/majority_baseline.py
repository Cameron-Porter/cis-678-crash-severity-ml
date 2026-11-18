import json
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier

from src.data.joins import CRASH_KEY, check_keys
from src.data.preprocess import sha256
from src.evaluation.evaluate import LABELS, evaluate_predictions


def fit_baselines(inputs):
    models = {}
    for configuration, item in inputs.items():
        matrix, rows = item['train']
        check_keys(rows, CRASH_KEY, 'training')
        if rows.empty or not rows.YEAR_FILE.isin([2020, 2021, 2022]).all():
            raise ValueError('Fit the baseline on 2020-2022 training rows only')
        if not rows.SEVERITY.isin(LABELS).all() or matrix.shape[0] != len(rows):
            raise ValueError('Invalid training labels or row alignment')
        models[configuration] = DummyClassifier(strategy='most_frequent').fit(matrix, rows.SEVERITY)
    return models


def evaluate_baselines(inputs, models):
    results = {}
    for configuration, model in models.items():
        matrix, rows = inputs[configuration]['validation']
        check_keys(rows, CRASH_KEY, 'validation')
        if rows.empty or not rows.YEAR_FILE.eq(2023).all():
            raise ValueError('Evaluate this baseline on 2023 validation only')
        predictions = model.predict(matrix)
        metrics, per_class, confusion = evaluate_predictions(rows.SEVERITY, predictions)
        output = rows[CRASH_KEY].copy()
        output['y_true'] = rows.SEVERITY.to_numpy()
        output['y_pred'] = predictions
        metrics.update(configuration=configuration, train_rows=len(inputs[configuration]['train'][1]),
                       validation_rows=len(rows), predicted_class=str(model.classes_[np.argmax(model.class_prior_)]))
        results[configuration] = {'metrics': metrics, 'per_class': per_class,
                                   'confusion': confusion, 'predictions': output}
    return results


def save_baseline_results(root, inputs, results):
    root = Path(root)
    report = root / 'results/majority_baseline'
    predictions = root / 'data/processed/predictions/majority_baseline'
    report.mkdir(parents=True, exist_ok=True)
    predictions.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([r['metrics'] for r in results.values()]).to_csv(report / 'metrics.csv', index=False, lineterminator='\n')
    for name in ('per_class', 'confusion'):
        pd.concat([r[name].assign(configuration=c) for c, r in results.items()], ignore_index=True).to_csv(
            report / f'{name}.csv', index=False, lineterminator='\n')
    hashes = {}
    for configuration, result in results.items():
        path = predictions / f'{configuration}_validation.csv'
        result['predictions'].to_csv(path, index=False, lineterminator='\n')
        hashes[path.relative_to(root).as_posix()] = sha256(path)
    run = {'model': 'DummyClassifier', 'strategy': 'most_frequent', 'sample_weight': None,
           'sklearn': sklearn.__version__, 'labels': list(LABELS), 'zero_division': 0,
           'fit_years': [2020, 2021, 2022], 'evaluation_year': 2023,
           'feature_metadata_sha256': {c: item['metadata_sha256'] for c, item in inputs.items()},
           'exclusions': {c: item['metadata']['exclusions'] for c, item in inputs.items()},
           'prediction_hashes': hashes,
           'source_hashes': {p.relative_to(root).as_posix(): sha256(p) for p in (
               root / 'src/models/majority_baseline.py', root / 'src/models/data.py', root / 'src/evaluation/evaluate.py')}}
    (report / 'run.json').write_text(json.dumps(run, indent=2, sort_keys=True)+'\n', encoding='utf8')

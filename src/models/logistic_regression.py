import json
import platform
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.data.joins import CRASH_KEY, check_keys
from src.data.preprocess import sha256
from src.evaluation.evaluate import LABELS, evaluate_predictions

PARAMETERS = dict(solver='lbfgs', C=1.0, l1_ratio=0.0, class_weight=None,
                  max_iter=1000, tol=1e-4, random_state=42)


def fit_logistic_models(inputs):
    models = {}
    for configuration, item in inputs.items():
        matrix, rows = item['train']
        check_keys(rows, CRASH_KEY, 'training')
        if rows.empty or not rows.YEAR_FILE.isin([2020, 2021, 2022]).all():
            raise ValueError('Fit Logistic Regression on 2020-2022 training rows only')
        if set(rows.SEVERITY) != set(LABELS) or matrix.shape[0] != len(rows):
            raise ValueError('Training requires all three severity classes and aligned rows')
        if not item['metadata']['scale_numeric']:
            raise ValueError('Logistic Regression requires scaled numeric features')
        model = LogisticRegression(**PARAMETERS)
        with warnings.catch_warnings():
            warnings.simplefilter('error', ConvergenceWarning)
            model.fit(matrix, rows.SEVERITY)
        models[configuration] = model
    return models


def evaluate_logistic_models(inputs, models):
    results = {}
    for configuration, model in models.items():
        matrix, rows = inputs[configuration]['validation']
        check_keys(rows, CRASH_KEY, 'validation')
        if rows.empty or not rows.YEAR_FILE.eq(2023).all():
            raise ValueError('Evaluate Logistic Regression on 2023 validation only')
        predicted = model.predict(matrix)
        metrics, per_class, confusion = evaluate_predictions(rows.SEVERITY, predicted)
        output = rows[CRASH_KEY].copy()
        output['y_true'] = rows.SEVERITY.to_numpy()
        output['y_pred'] = predicted
        probabilities = model.predict_proba(matrix)
        for label in LABELS:
            output[f'p_{label}'] = probabilities[:, list(model.classes_).index(label)]
        metrics.update(configuration=configuration, train_rows=len(inputs[configuration]['train'][1]),
                       validation_rows=len(rows), iterations=int(model.n_iter_.max()))
        results[configuration] = dict(metrics=metrics, per_class=per_class, confusion=confusion, predictions=output)
    return results


def save_logistic_results(root, inputs, models, results):
    root = Path(root)
    report = root / 'results/logistic_regression'
    local = root / 'data/processed/predictions/logistic_regression'
    pipelines = {}
    for configuration, model in models.items():
        folder = root / 'data/processed/features' / configuration
        metadata = inputs[configuration]['metadata']
        path = folder / 'preprocessor.joblib'
        if sha256(path) != metadata['files'][path.name]:
            raise ValueError('Preprocessor hash mismatch; rerun prepare_features.py')
        if metadata['sklearn'] != sklearn.__version__:
            raise ValueError('Rebuild features with the current scikit-learn version')
        preprocessor = joblib.load(path)
        pipelines[configuration] = Pipeline([('preprocess', preprocessor), ('model', model)])
    report.mkdir(parents=True, exist_ok=True)
    local.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([r['metrics'] for r in results.values()]).to_csv(report / 'metrics.csv', index=False, lineterminator='\n')
    for name in ('per_class', 'confusion'):
        pd.concat([r[name].assign(configuration=c) for c, r in results.items()], ignore_index=True).to_csv(
            report / f'{name}.csv', index=False, lineterminator='\n')
    hashes = {}
    for configuration, result in results.items():
        path = local / f'{configuration}_validation.csv'
        result['predictions'].to_csv(path, index=False, lineterminator='\n')
        hashes[path.relative_to(root).as_posix()] = sha256(path)
        joblib.dump(pipelines[configuration], local / f'{configuration}_pipeline.joblib')
    run = dict(model='LogisticRegression', parameters={c: m.get_params() for c, m in models.items()},
               versions=dict(python=platform.python_version(), sklearn=sklearn.__version__, numpy=np.__version__,
                             pandas=pd.__version__, scipy=scipy.__version__),
               labels=list(LABELS), zero_division=0, fit_years=[2020, 2021, 2022], evaluation_year=2023,
               sample_weight=None, feature_metadata_sha256={c: i['metadata_sha256'] for c, i in inputs.items()},
               exclusions={c: i['metadata']['exclusions'] for c, i in inputs.items()}, prediction_hashes=hashes,
               source_hashes={p.relative_to(root).as_posix(): sha256(p) for p in (
                   root / 'src/models/logistic_regression.py', root / 'src/models/data.py', root / 'src/evaluation/evaluate.py')})
    (report / 'run.json').write_text(json.dumps(run, indent=2, sort_keys=True)+'\n', encoding='utf8')

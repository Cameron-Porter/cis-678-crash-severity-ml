import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

import numpy as np
import pandas as pd

from src.data.joins import CRASH_KEY, check_keys
from src.data.preprocess import sha256
from src.evaluation.evaluate import LABELS, evaluate_predictions

RUNS = ('majority_baseline', 'logistic_regression', 'baseline_tuning')


def validate_predictions(frame):
    check_keys(frame, CRASH_KEY, 'validation predictions')
    if frame.empty or not frame.YEAR_FILE.eq(2023).all():
        raise ValueError('Handoff requires nonempty 2023 validation predictions')
    if not frame.y_true.isin(LABELS).all() or not frame.y_pred.isin(LABELS).all():
        raise ValueError('Handoff contains invalid severity labels')
    probabilities = frame[[f'p_{label}' for label in LABELS]].to_numpy()
    if not np.isfinite(probabilities).all() or (probabilities < 0).any() or (probabilities > 1).any():
        raise ValueError('Invalid probabilities')
    if not np.allclose(probabilities.sum(axis=1), 1, rtol=0, atol=1e-10):
        raise ValueError('Probabilities must sum to one')
    chosen = np.array([LABELS.index(label) for label in frame.y_pred])
    if not np.allclose(probabilities[np.arange(len(frame)), chosen], probabilities.max(axis=1), rtol=0, atol=1e-10):
        raise ValueError('Predicted class does not maximize probability')


def collect_handoff(root):
    root = Path(root)
    predictions, metrics, per_class, confusion, configurations = [], [], [], [], []
    runs, reference, feature_hashes = {}, None, None
    for name in RUNS:
        folder = root / 'results' / name
        run = json.loads((folder / 'run.json').read_text(encoding='utf8'))
        if run['fit_years'] != [2020, 2021, 2022] or run['evaluation_year'] != 2023 or run['labels'] != list(LABELS):
            raise ValueError('Run does not match the baseline split and label contract')
        if feature_hashes is not None and feature_hashes != run['feature_metadata_sha256']:
            raise ValueError('Baseline runs use different feature artifacts')
        feature_hashes = run['feature_metadata_sha256']
        runs[name] = run
        recorded = pd.read_csv(folder / 'metrics.csv').set_index('configuration')
        for configuration in ('core', 'expanded'):
            model_id = f'{name}_{configuration}'
            relative = f'data/processed/predictions/{name}/{configuration}_validation.csv'
            path = root / relative
            if sha256(path) != run['prediction_hashes'][relative]:
                raise ValueError(f'Prediction hash mismatch: {model_id}')
            frame = pd.read_csv(path, float_precision='round_trip')
            if name == 'majority_baseline':
                for label in LABELS:
                    frame[f'p_{label}'] = frame.y_pred.eq(label).astype(float)
            validate_predictions(frame)
            aligned = frame[CRASH_KEY + ['y_true']]
            if reference is not None:
                pd.testing.assert_frame_equal(reference, aligned)
            reference = aligned
            counts = run['exclusions'][configuration]
            if counts['validation']['eligible_rows'] != len(frame):
                raise ValueError('Validation exclusions disagree with predictions')
            summary, classes, matrix = evaluate_predictions(frame.y_true, frame.y_pred)
            for metric, value in summary.items():
                if not np.isclose(value, recorded.loc[configuration, metric], rtol=0, atol=1e-12):
                    raise ValueError(f'Recorded metrics disagree with predictions: {model_id}')
            predictions.append(frame.assign(model_id=model_id))
            metrics.append(dict(model_id=model_id, **summary, validation_rows=len(frame)))
            per_class.append(classes.assign(model_id=model_id))
            confusion.append(matrix.assign(model_id=model_id))
            selected = name == 'baseline_tuning'
            configurations.append(dict(model_id=model_id, configuration=configuration, estimator=run['model'],
                parameters=run['parameters'][configuration] if name != 'majority_baseline' else {'strategy': run['strategy']},
                selected_per_feature_set=selected,
                overall_logistic_winner=selected and configuration == run['search']['winner']['configuration'],
                exclusions=counts))
    return dict(predictions=pd.concat(predictions, ignore_index=True), metrics=pd.DataFrame(metrics),
                per_class=pd.concat(per_class, ignore_index=True), confusion=pd.concat(confusion, ignore_index=True),
                configurations=configurations, runs=runs)


def save_handoff(root, handoff):
    root = Path(root)
    local = root / 'data/processed/baseline_handoff'
    report = root / 'results/baseline_handoff'
    local.mkdir(parents=True, exist_ok=True)
    report.mkdir(parents=True, exist_ok=True)
    payloads = {}
    for name in ('predictions', 'metrics', 'per_class', 'confusion'):
        payloads[f'{name}.csv'] = handoff[name].to_csv(index=False, lineterminator='\n').encode('utf8')
    payloads['labels.csv'] = pd.DataFrame({'label': LABELS, 'probability_column': [f'p_{l}' for l in LABELS]}).to_csv(index=False, lineterminator='\n').encode('utf8')
    config = dict(schema_version=1, target='SEVERITY', fit_years=[2020, 2021, 2022], evaluation_year=2023,
                  labels=list(LABELS), selection_metric='macro_f1', refit_on_validation=False,
                  models=handoff['configurations'], search=handoff['runs']['baseline_tuning']['search'])
    payloads['configurations.json'] = (json.dumps(config, indent=2, sort_keys=True)+'\n').encode('utf8')
    payloads['source_runs.json'] = (json.dumps(handoff['runs'], indent=2, sort_keys=True)+'\n').encode('utf8')
    for name, data in payloads.items():
        (local / name).write_bytes(data)
        if name not in ('predictions.csv', 'source_runs.json'):
            (report / name).write_bytes(data)
    manifest = dict(schema_version=1, files={name: sha256(local / name) for name in payloads},
                    exporter_sha256=sha256(root / 'src/evaluation/export_baselines.py'))
    payloads['manifest.json'] = (json.dumps(manifest, indent=2, sort_keys=True)+'\n').encode('utf8')
    (local / 'manifest.json').write_bytes(payloads['manifest.json'])
    (report / 'manifest.json').write_bytes(payloads['manifest.json'])
    archive = root / 'data/processed/baseline_handoff.zip'
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as zipped:
        for name, data in sorted(payloads.items()):
            entry = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            zipped.writestr(entry, data)
    return archive

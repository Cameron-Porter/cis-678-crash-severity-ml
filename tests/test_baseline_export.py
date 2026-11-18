import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from src.data.preprocess import sha256
from src.evaluation.evaluate import evaluate_predictions
from src.evaluation.export_baselines import RUNS, collect_handoff, save_handoff, validate_predictions


class BaselineExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / 'src/evaluation/export_baselines.py'
        source.parent.mkdir(parents=True)
        source.write_text('fixture')
        self.frame = pd.DataFrame(dict(YEAR_FILE=[2023]*3, CASENUM=[1, 2, 3],
            y_true=['low', 'moderate', 'high'], y_pred=['moderate']*3,
            p_low=[0.]*3, p_moderate=[1.]*3, p_high=[0.]*3))
        for name in RUNS:
            report = self.root / 'results' / name
            local = self.root / 'data/processed/predictions' / name
            report.mkdir(parents=True)
            local.mkdir(parents=True)
            run = dict(fit_years=[2020, 2021, 2022], evaluation_year=2023, labels=['low', 'moderate', 'high'],
                       feature_metadata_sha256={'core': 'a', 'expanded': 'b'}, prediction_hashes={}, exclusions={},
                       model='DummyClassifier' if name == 'majority_baseline' else 'LogisticRegression',
                       strategy='most_frequent', parameters={}, search={'winner': {'configuration': 'expanded'}})
            metrics = []
            for configuration in ('core', 'expanded'):
                path = local / f'{configuration}_validation.csv'
                self.frame.to_csv(path, index=False)
                run['prediction_hashes'][path.relative_to(self.root).as_posix()] = sha256(path)
                run['exclusions'][configuration] = {'validation': {'eligible_rows': 3}}
                run['parameters'][configuration] = {'C': 1}
                metrics.append(dict(configuration=configuration, **evaluate_predictions(self.frame.y_true, self.frame.y_pred)[0]))
            (report / 'run.json').write_text(json.dumps(run))
            pd.DataFrame(metrics).to_csv(report / 'metrics.csv', index=False)

    def test_export_roundtrip_and_reproducible_archive(self):
        handoff = collect_handoff(self.root)
        self.assertEqual(len(handoff['predictions']), 18)
        self.assertEqual(len(handoff['metrics']), 6)
        archive = save_handoff(self.root, handoff)
        first = archive.read_bytes()
        save_handoff(self.root, handoff)
        self.assertEqual(first, archive.read_bytes())
        with ZipFile(archive) as zipped:
            frame = pd.read_csv(zipped.open('predictions.csv'))
            pd.testing.assert_frame_equal(frame, handoff['predictions'])
            self.assertIn('source_runs.json', zipped.namelist())
        self.assertFalse((self.root / 'results/baseline_handoff/predictions.csv').exists())

    def test_rejects_tampered_predictions(self):
        path = self.root / 'data/processed/predictions/baseline_tuning/core_validation.csv'
        path.write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            collect_handoff(self.root)

    def test_rejects_inconsistent_reported_metrics(self):
        path = self.root / 'results/logistic_regression/metrics.csv'
        frame = pd.read_csv(path)
        frame['accuracy'] = 1
        frame.to_csv(path, index=False)
        with self.assertRaisesRegex(ValueError, 'metrics disagree'):
            collect_handoff(self.root)

    def test_rejects_test_year_duplicates_and_invalid_probabilities(self):
        for column, value in [('YEAR_FILE', 2024), ('CASENUM', 1), ('y_true', 'unknown'),
                              ('p_high', .5), ('p_low', float('nan')), ('y_pred', 'high')]:
            frame = self.frame.copy()
            frame[column] = value
            with self.assertRaises(ValueError):
                validate_predictions(frame)


if __name__ == '__main__':
    unittest.main()

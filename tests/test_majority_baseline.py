import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, save_npz

from src.data.preprocess import sha256
from src.models.data import load_baseline_inputs

from src.evaluation.evaluate import evaluate_predictions
from src.models.majority_baseline import fit_baselines, evaluate_baselines


def fixture():
    train = pd.DataFrame({'YEAR_FILE': [2020, 2021, 2022], 'CASENUM': [1, 1, 1],
                          'SEVERITY': ['low', 'low', 'moderate']})
    validation = pd.DataFrame({'YEAR_FILE': [2023]*4, 'CASENUM': [1, 2, 3, 4],
                               'SEVERITY': ['high', 'high', 'high', 'low']})
    return {c: {'train': (csr_matrix(np.ones((3, width))), train.copy()),
                'validation': (csr_matrix(np.ones((4, width))), validation.copy())}
            for c, width in [('core', 2), ('expanded', 4)]}


class BaselineArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        processed = self.root / 'data/processed'
        processed.mkdir(parents=True)
        (processed / 'manifest.json').write_text('{}')
        for configuration, item in fixture().items():
            folder = processed / 'features' / configuration
            folder.mkdir(parents=True)
            exclusions = {}
            for split, (matrix, rows) in item.items():
                save_npz(folder / f'{split}.npz', matrix)
                rows.to_csv(folder / f'{split}_rows.csv', index=False)
                exclusions[split] = dict(input_rows=len(rows), eligible_rows=len(rows), excluded_unknown=0)
            pd.DataFrame({'feature': [f'x{i}' for i in range(matrix.shape[1])]}).to_csv(folder / 'columns.csv', index=False)
            metadata = dict(configuration=configuration, fit_years=[2020, 2021, 2022],
                            processed_manifest_sha256=sha256(processed / 'manifest.json'), exclusions=exclusions,
                            files={p.name: sha256(p) for p in folder.iterdir()})
            (folder / 'metadata.json').write_text(json.dumps(metadata))

    def test_loads_without_test_data_and_rejects_modified_artifact(self):
        inputs = load_baseline_inputs(self.root)
        self.assertEqual(inputs['core']['validation'][0].shape, (4, 2))
        path = self.root / 'data/processed/features/core/train_rows.csv'
        path.write_text(path.read_text().replace('low', 'high'))
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            load_baseline_inputs(self.root)

    def test_rejects_different_crash_order_between_configurations(self):
        folder = self.root / 'data/processed/features/expanded'
        path = folder / 'validation_rows.csv'
        pd.read_csv(path).iloc[::-1].to_csv(path, index=False)
        metadata_path = folder / 'metadata.json'
        metadata = json.loads(metadata_path.read_text())
        metadata['files'][path.name] = sha256(path)
        metadata_path.write_text(json.dumps(metadata))
        with self.assertRaises(AssertionError):
            load_baseline_inputs(self.root)


class MajorityBaselineTests(unittest.TestCase):
    def test_training_majority_ignores_validation_distribution_and_features(self):
        inputs = fixture()
        models = fit_baselines(inputs)
        results = evaluate_baselines(inputs, models)
        for result in results.values():
            self.assertEqual(result['predictions'].y_pred.tolist(), ['low']*4)
            self.assertEqual(result['metrics']['accuracy'], .25)
            self.assertAlmostEqual(result['metrics']['macro_f1'], .4/3)
            self.assertEqual(result['metrics']['high_severity_recall'], 0)
        pd.testing.assert_frame_equal(results['core']['predictions'], results['expanded']['predictions'])
        again = evaluate_baselines(inputs, fit_baselines(inputs))
        pd.testing.assert_frame_equal(results['core']['predictions'], again['core']['predictions'])

    def test_holdout_fit_and_test_evaluation_are_rejected(self):
        inputs = fixture()
        inputs['core']['train'][1]['YEAR_FILE'] = 2023
        with self.assertRaises(ValueError): fit_baselines(inputs)
        inputs = fixture()
        models = fit_baselines(inputs)
        inputs['core']['validation'][1]['YEAR_FILE'] = 2024
        with self.assertRaises(ValueError): evaluate_baselines(inputs, models)

    def test_unknown_training_labels_rejected(self):
        inputs = fixture()
        inputs['core']['train'][1].loc[0, 'SEVERITY'] = 'unknown'
        with self.assertRaises(ValueError): fit_baselines(inputs)

    def test_ties_follow_sorted_sklearn_class_order(self):
        inputs = fixture()
        inputs['core']['train'][1]['SEVERITY'] = ['low', 'high', 'moderate']
        result = evaluate_baselines(inputs, fit_baselines(inputs))
        self.assertEqual(result['core']['predictions'].y_pred.tolist(), ['high']*4)

    def test_metrics_include_absent_classes_and_fixed_confusion_order(self):
        metrics, per_class, confusion = evaluate_predictions(['low', 'low'], ['low', 'low'])
        self.assertEqual(metrics['accuracy'], 1)
        self.assertAlmostEqual(metrics['macro_f1'], 1/3)
        self.assertEqual(per_class.label.tolist(), ['low', 'moderate', 'high'])
        self.assertEqual(per_class.support.tolist(), [2, 0, 0])
        self.assertEqual(len(confusion), 9)
        self.assertEqual(confusion.rows.sum(), 2)
        self.assertEqual(confusion.iloc[0]['rows'], 2)

    def test_invalid_evaluation_labels_and_lengths_rejected(self):
        for actual, predicted in [([], []), (['low'], []), (['unknown'], ['low']), (['low'], ['invalid'])]:
            with self.assertRaises(ValueError): evaluate_predictions(actual, predicted)


if __name__ == '__main__':
    unittest.main()

import unittest
import warnings
from unittest.mock import patch

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.exceptions import ConvergenceWarning

from src.models.logistic_regression import fit_logistic_models, evaluate_logistic_models


def fixture():
    labels = ['low', 'moderate', 'high'] * 20
    train = pd.DataFrame({'YEAR_FILE': [2020, 2021, 2022] * 20,
                          'CASENUM': np.arange(60), 'SEVERITY': labels})
    validation = train.iloc[:6].copy().assign(YEAR_FILE=2023)
    matrix = csr_matrix(np.tile(np.eye(3), (20, 1)) * 10)
    return {c: dict(train=(matrix.copy(), train.copy()), validation=(matrix[:6].copy(), validation.copy()),
                    metadata={'scale_numeric': True}) for c in ('core', 'expanded')}


class LogisticRegressionTests(unittest.TestCase):
    def test_learns_three_classes_and_probability_columns_match_labels(self):
        inputs = fixture()
        models = fit_logistic_models(inputs)
        results = evaluate_logistic_models(inputs, models)
        for c, result in results.items():
            self.assertEqual(result['metrics']['macro_f1'], 1)
            output = result['predictions']
            np.testing.assert_allclose(output[['p_low', 'p_moderate', 'p_high']].sum(axis=1), 1)
            self.assertEqual(output[['p_low', 'p_moderate', 'p_high']].idxmax(axis=1).str[2:].tolist(), output.y_pred.tolist())
            self.assertEqual(models[c].coef_.shape, (3, 3))
        inputs['core']['validation'][1]['SEVERITY'] = 'high'
        again = fit_logistic_models(inputs)
        np.testing.assert_array_equal(models['core'].coef_, again['core'].coef_)

    def test_holdout_fit_and_test_evaluation_rejected(self):
        inputs = fixture()
        inputs['core']['train'][1]['YEAR_FILE'] = 2023
        with self.assertRaises(ValueError):
            fit_logistic_models(inputs)
        inputs = fixture()
        models = fit_logistic_models(inputs)
        inputs['core']['validation'][1]['YEAR_FILE'] = 2024
        with self.assertRaises(ValueError):
            evaluate_logistic_models(inputs, models)

    def test_requires_all_classes_and_scaled_features(self):
        for invalid in ('unknown', 'low'):
            inputs = fixture()
            inputs['core']['train'][1]['SEVERITY'] = invalid
            with self.assertRaises(ValueError):
                fit_logistic_models(inputs)
        inputs = fixture()
        inputs['core']['metadata']['scale_numeric'] = False
        with self.assertRaises(ValueError):
            fit_logistic_models(inputs)

    def test_nonconvergence_stops_run(self):
        def fail(*args, **kwargs):
            warnings.warn('did not converge', ConvergenceWarning)
        with patch('src.models.logistic_regression.LogisticRegression.fit', side_effect=fail):
            with self.assertRaises(ConvergenceWarning):
                fit_logistic_models(fixture())


if __name__ == '__main__':
    unittest.main()

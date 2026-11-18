import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from test_logistic_regression import fixture
from src.models.tune_baselines import rank_candidates, tune_baselines


class BaselineTuningTests(unittest.TestCase):
    def test_selection_uses_macro_f1_and_fixed_tie_rule(self):
        rows = [dict(configuration=c, C=C, class_weight=w, macro_f1=.5, accuracy=.6)
                for c in ('expanded', 'core') for C in (10, .1) for w in ('balanced', 'unweighted')]
        rows.append(dict(configuration='expanded', C=1, class_weight='balanced', macro_f1=.4, accuracy=.99))
        ranked = rank_candidates(pd.DataFrame(rows))
        self.assertEqual(ranked.iloc[0][['configuration', 'C', 'class_weight']].tolist(), ['core', .1, 'unweighted'])
        self.assertEqual(ranked.iloc[-1].accuracy, .99)
        pd.testing.assert_frame_equal(ranked, rank_candidates(pd.DataFrame(rows).sample(frac=1, random_state=42)))

    def test_search_covers_both_weights_and_retains_selected_models(self):
        inputs = fixture()
        with patch('src.models.tune_baselines.C_VALUES', (.1, 1.0)):
            tuning = tune_baselines(inputs)
        candidates = tuning['candidates']
        self.assertEqual(len(candidates), 8)
        self.assertEqual(set(candidates.class_weight), {'unweighted', 'balanced'})
        self.assertEqual(len(tuning['per_class']), 24)
        self.assertEqual(len(tuning['confusion']), 72)
        for configuration, model in tuning['models'].items():
            expected = rank_candidates(candidates[candidates.configuration.eq(configuration)]).iloc[0]
            self.assertEqual(model.C, expected.C)
            self.assertEqual(model.class_weight or 'unweighted', expected.class_weight)
            self.assertEqual(tuning['results'][configuration]['metrics']['macro_f1'], expected.macro_f1)
            np.testing.assert_array_equal(model.predict(inputs[configuration]['validation'][0]),
                                          tuning['results'][configuration]['predictions'].y_pred)
        self.assertEqual(tuning['winner'], candidates.iloc[0].to_dict())
        self.assertEqual(set(tuning['comparison'].model), {'majority', 'tuned_logistic_regression'})

    def test_tuning_rejects_test_year_in_validation(self):
        inputs = fixture()
        inputs['core']['validation'][1]['YEAR_FILE'] = 2024
        with self.assertRaises(ValueError):
            tune_baselines(inputs)


if __name__ == '__main__':
    unittest.main()

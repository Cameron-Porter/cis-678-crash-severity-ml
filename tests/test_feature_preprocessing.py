import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone

from src.features.build_features import build_feature_table, CORE_CATEGORICAL, EXPANDED_FEATURES
from src.features.preprocessing import make_preprocessor


def raw_fixture():
    crashes = pd.DataFrame({'YEAR_FILE': [2020]*3, 'CASENUM': [1, 2, 3], 'VE_TOTAL': [2, 1, 1]})
    for name in CORE_CATEGORICAL:
        crashes[name] = 1
    vehicle = pd.DataFrame({'YEAR_FILE': [2020]*3, 'CASENUM': [1, 1, 2], 'VEH_NO': [1, 2, 1],
                            'MOD_YEAR': [2010, 2021, 9999], 'SPEEDREL': [0, 9, 3]})
    person = pd.DataFrame({'YEAR_FILE': [2020]*4, 'CASENUM': [1, 1, 1, 2], 'VEH_NO': [1, 1, 2, 1],
                           'PER_NO': [1, 2, 1, 1], 'PER_TYP': [2, 1, 1, 1],
                           'AGE': [3, 40, 998, 60], 'DRINKING': [1, 0, 9, 1]})
    return crashes, vehicle, person


def constructed_fixture():
    frame = pd.DataFrame({name: [1., 2., 3.] for name in EXPANDED_FEATURES})
    frame['YEAR_FILE'] = [2020, 2021, 2022]
    frame['CASENUM'] = [1, 1, 1]
    frame['VEHICLE_AGE_MIN'] = [0., np.nan, 10.]
    frame['VEHICLE_AGE_MAX'] = np.nan
    frame['WEATHER'] = np.nan
    return frame


def dense(matrix):
    return matrix.toarray() if hasattr(matrix, 'toarray') else matrix


class FeatureConstructionTests(unittest.TestCase):
    def test_driver_selection_partial_unknown_and_no_records(self):
        result = build_feature_table(*raw_fixture()).set_index('CASENUM')
        self.assertEqual(result.loc[1, 'VEHICLE_AGE_MIN'], 0)
        self.assertEqual(result.loc[1, 'VEHICLE_AGE_MAX'], 10)
        self.assertEqual(result.loc[1, 'DRIVER_AGE_MIN'], 40)
        self.assertTrue(np.isnan(result.loc[1, 'DRINKING_ANY']))
        self.assertTrue(np.isnan(result.loc[1, 'SPEEDING_ANY']))
        self.assertEqual(result.loc[2, 'DRINKING_ANY'], 1)
        self.assertEqual(result.loc[2, 'SPEEDING_ANY'], 1)
        self.assertTrue(result.loc[3, ['VEHICLE_AGE_MIN', 'DRIVER_AGE_MIN', 'DRINKING_ANY', 'SPEEDING_ANY']].isna().all())

    def test_positive_wins_and_negative_requires_all_known(self):
        a, v, p = raw_fixture()
        v.loc[0, 'SPEEDREL'] = 2
        p.loc[1, 'DRINKING'] = 1
        result = build_feature_table(a, v, p)
        self.assertEqual(result.loc[0, 'SPEEDING_ANY'], 1)
        self.assertEqual(result.loc[0, 'DRINKING_ANY'], 1)
        v.SPEEDREL = 0
        p.DRINKING = 0
        result = build_feature_table(a, v, p)
        self.assertEqual(result.loc[0, 'SPEEDING_ANY'], 0)
        self.assertEqual(result.loc[0, 'DRINKING_ANY'], 0)

    def test_missing_codes_partial_categories_and_invalid_values(self):
        a, v, p = raw_fixture()
        a.loc[0, ['WEATHER', 'LGT_COND', 'HOUR']] = [8, 6, 99]
        result = build_feature_table(a, v, p)
        self.assertEqual(result.loc[0, 'WEATHER'], 8)
        self.assertEqual(result.loc[0, 'LGT_COND'], 6)
        self.assertTrue(np.isnan(result.loc[0, 'HOUR']))
        for invalid in (9, 1.5, 'bad'):
            a.WEATHER = invalid
            with self.assertRaises(ValueError): build_feature_table(a, v, p)

    def test_keys_order_unmatched_driver_and_outcomes(self):
        a, v, p = raw_fixture()
        p.loc[1, 'VEH_NO'] = 99  # Keep the driver's crash contribution.
        a = a.iloc[::-1]
        baseline = build_feature_table(a, v, p)
        self.assertEqual(baseline.CASENUM.tolist(), [3, 2, 1])
        a['SEVERITY'] = 'high'; v['TOWED'] = 2; p['INJ_SEV'] = 4
        pd.testing.assert_frame_equal(baseline, build_feature_table(a, v, p))
        v.loc[0, 'CASENUM'] = 999
        with self.assertRaises(ValueError): build_feature_table(a, v, p)


class PreprocessingTests(unittest.TestCase):
    def test_fit_rejects_holdout_missing_year_and_empty(self):
        frame = constructed_fixture()
        for bad in (frame.assign(YEAR_FILE=2023), frame.assign(YEAR_FILE=2024), frame.drop(columns='YEAR_FILE'), frame.iloc[:0]):
            with self.assertRaises(ValueError): make_preprocessor().fit(bad)

    def test_unknown_categories_empty_columns_and_training_statistics(self):
        train = constructed_fixture()
        holdout = train.assign(YEAR_FILE=2024, MONTH=12, WEATHER=8, VEHICLE_AGE_MIN=999)
        for configuration in ('core', 'expanded'):
            pipe = make_preprocessor(configuration)
            fitted = pipe.fit_transform(train)
            numeric = pipe.named_steps['columns'].named_transformers_['numeric']
            before = numeric.named_steps['impute'].statistics_.copy()
            means = numeric.named_steps['scale'].mean_.copy()
            names = pipe.get_feature_names_out().copy()
            transformed = pipe.transform(holdout)
            self.assertEqual(fitted.shape, transformed.shape)
            self.assertTrue(np.isfinite(dense(transformed)).all())
            np.testing.assert_array_equal(before, numeric.named_steps['impute'].statistics_)
            np.testing.assert_array_equal(means, numeric.named_steps['scale'].mean_)
            np.testing.assert_array_equal(names, pipe.get_feature_names_out())
            self.assertEqual(before[1], 5)  # Median learned only from training ages.
            self.assertEqual(before[2], 0)  # All-empty training feature retained.
            self.assertFalse(any('YEAR_FILE' in n or 'CASENUM' in n for n in names))

    def test_serialization_cloning_and_unscaled_option(self):
        frame = constructed_fixture()
        pipe = clone(make_preprocessor('expanded', scale_numeric=False))
        expected = pipe.fit_transform(frame)
        names = pipe.get_feature_names_out()
        index = list(names).index('numeric__VEHICLE_AGE_MIN')
        np.testing.assert_array_equal(dense(expected)[:, index], [0, 5, 10])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'pipeline.joblib'
            joblib.dump(pipe, path)
            loaded = joblib.load(path)
            np.testing.assert_array_equal(dense(expected), dense(loaded.transform(frame)))


if __name__ == '__main__':
    unittest.main()

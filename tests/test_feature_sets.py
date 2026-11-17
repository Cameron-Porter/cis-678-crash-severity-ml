
import csv
import unittest
from pathlib import Path

import pandas as pd

from src.features.build_features import (
    CORE_FEATURES, EXPANDED_FEATURES, feature_columns, select_features,
)


class FeatureContractTests(unittest.TestCase):
    def test_outcomes_metadata_and_unreviewed_fields_never_reach_models(self):
        frame = pd.DataFrame({column: [1, 2] for column in EXPANDED_FEATURES})
        for column in ('SEVERITY', 'INJ_SEV', 'TOWED', 'DEFORMED', 'STRATUM',
                       'YEAR_FILE', 'CASENUM', 'WEIGHT', 'AGE_IM', 'FUTURE_RAW_FIELD'):
            frame[column] = [0, 1]
        frame.index = [20, 10]
        for configuration in ('core', 'expanded'):
            result = select_features(frame, configuration)
            self.assertEqual(tuple(result.columns), feature_columns(configuration))
            self.assertEqual(result.index.tolist(), [20, 10])
            self.assertEqual(len(result), len(frame))
            result.iloc[0, 0] = 99
            self.assertEqual(frame.iloc[0, 0], 1)

    def test_missing_aggregates_and_ambiguous_inputs_fail(self):
        frame = pd.DataFrame({column: [1] for column in EXPANDED_FEATURES})
        with self.assertRaisesRegex(ValueError, 'Missing constructed features'):
            select_features(frame.drop(columns='VEHICLE_AGE_MIN'), 'core')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            select_features(pd.concat([frame, frame[['MONTH']]], axis=1), 'core')
        with self.assertRaisesRegex(ValueError, 'configuration'):
            select_features(frame, 'expaned')

    def test_published_catalog_matches_shared_contract(self):
        path = Path(__file__).resolve().parents[1] / 'docs/crss_feature_sets.csv'
        with path.open(encoding='utf8', newline='') as stream:
            catalog = list(csv.DictReader(stream))
        self.assertEqual(tuple(row['feature'] for row in catalog), EXPANDED_FEATURES)
        self.assertEqual(tuple(row['feature'] for row in catalog if row['configuration']=='core;expanded'), CORE_FEATURES)
        for row in catalog:
            for field in ('source_columns', 'construction', 'missing_rule', 'rationale',
                          'availability', 'outcome_review', 'manual_url', 'printed_pages'):
                self.assertTrue(row[field], (row['feature'], field))
        self.assertEqual(EXPANDED_FEATURES[:len(CORE_FEATURES)], CORE_FEATURES)
        self.assertEqual(len(set(EXPANDED_FEATURES)), len(EXPANDED_FEATURES))


if __name__ == '__main__':
    unittest.main()

"""Protect chronological splits and the processed-file contract."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data.preprocess import (OUTPUT_COLUMNS, processed_schema, read_processed_csv,
                                 split_crashes, validate_splits)


def fixture():
    rows = []
    for year in range(2020, 2025):
        for number in (1, 2):
            row = {column: 0 for column in OUTPUT_COLUMNS}
            row.update(YEAR=year, YEAR_FILE=year, CASENUM=number, SEVERITY="unknown",
                       WRK_ZONENAME="None", WEIGHT=1.2345678901234567)
            rows.append(row)
    return pd.DataFrame(rows)


class ProcessedDataTests(unittest.TestCase):
    def test_split_order_and_repeated_case_numbers_across_years(self):
        source = fixture().sample(frac=1, random_state=42)
        splits = split_crashes(source)
        self.assertEqual([len(f) for f in splits.values()], [6, 2, 2])
        self.assertEqual(splits['train'].CASENUM.tolist(), [1, 2, 1, 2, 1, 2])

    def test_omitted_crash_is_rejected(self):
        source = fixture(); splits = split_crashes(source)
        splits['train'] = splits['train'].iloc[1:]
        with self.assertRaises(AssertionError):
            validate_splits(splits, source)

    def test_duplicate_or_cross_split_crash_is_rejected(self):
        source = fixture()
        for destination in ('train', 'test'):
            with self.subTest(destination=destination):
                splits = split_crashes(source)
                splits[destination] = pd.concat([splits[destination], splits['train'].iloc[:1]])
                with self.assertRaises(ValueError):
                    validate_splits(splits, source)

    def test_unknown_year_label_and_schema_are_rejected(self):
        for change in ('year', 'label', 'schema', 'folder'):
            with self.subTest(change=change):
                source = fixture(); splits = split_crashes(source)
                if change == 'year': splits['test'].loc[0, 'YEAR_FILE'] = 2025
                if change == 'label': splits['test'].loc[0, 'SEVERITY'] = 'invalid'
                if change == 'schema': splits['test']['SEVERITY_REASON'] = 'leakage'
                if change == 'folder': splits['test'].loc[0, 'YEAR'] = 2023
                with self.assertRaises(ValueError):
                    validate_splits(splits, source)

    def test_changed_values_are_rejected(self):
        source = fixture(); splits = split_crashes(source)
        splits['train'].loc[0, 'WRK_ZONENAME'] = 'changed'
        with self.assertRaises(AssertionError):
            validate_splits(splits, source)

    def test_saved_csv_preserves_text_blanks_and_weights(self):
        source = fixture()
        source.loc[0, 'WRK_ZONENAME'] = pd.NA
        schema = processed_schema(source)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'processed.csv'
            source.to_csv(path, index=False)
            result = read_processed_csv(path, schema)
        pd.testing.assert_frame_equal(source, result, check_dtype=False)
        self.assertEqual(result.loc[1, 'WRK_ZONENAME'], 'None')
        self.assertTrue(pd.isna(result.loc[0, 'WRK_ZONENAME']))
        self.assertEqual(source.loc[0, 'WEIGHT'], result.loc[0, 'WEIGHT'])


if __name__ == '__main__':
    unittest.main()

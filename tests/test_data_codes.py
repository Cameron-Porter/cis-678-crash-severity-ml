"""Check parsing, code-year boundaries, and diagnostic flags."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data.audit_codes import audit_table, coding_changes, label_kind, validate_codes
from src.data.load import read_raw_csv


class DataCodeTests(unittest.TestCase):
    def test_literal_none_and_na_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.csv"
            path.write_text('WRK_ZONE,WRK_ZONENAME\n0,None\n1,NA\n2,\n', encoding="latin-1")
            frame = read_raw_csv(path)
            self.assertEqual(frame.loc[0, "WRK_ZONENAME"], "None")
            self.assertEqual(frame.loc[1, "WRK_ZONENAME"], "NA")
            self.assertTrue(pd.isna(frame.loc[2, "WRK_ZONENAME"]))

    def test_case_collision_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.csv"
            path.write_text('V_Config,V_CONFIG\n1,2\n', encoding="latin-1")
            with self.assertRaisesRegex(ValueError, "collide"):
                read_raw_csv(path)

    def test_year_specific_towing_and_damage(self):
        old = pd.DataFrame({"TOWED": ["2", "3", "7"], "DEFORMED": ["0", "2", "6"]})
        new = pd.DataFrame({"TOWED": ["6"], "DEFORMED": ["7"]})
        self.assertEqual(sum(c["rows"] for c in validate_codes(old, "vehicle", 2020)), 0)
        self.assertEqual(sum(c["rows"] for c in validate_codes(new, "vehicle", 2022)), 0)
        self.assertEqual(sum(c["rows"] for c in validate_codes(new, "vehicle", 2020)), 2)
        self.assertEqual(sum(c["rows"] for c in validate_codes(old, "vehicle", 2022)), 3)

    def test_missing_categories_are_not_global_numeric_codes(self):
        frame = pd.DataFrame({"WRK_ZONE": ["0", "4"], "LGT_COND": ["8", "9"], "WEATHER": ["8", "99"]})
        self.assertEqual(sum(c["rows"] for c in validate_codes(frame, "accident", 2024)), 0)
        self.assertEqual(label_kind("None"), "other")
        self.assertEqual(label_kind("Other"), "other")
        self.assertEqual(label_kind("Dark - Unknown Lighting"), "partly_unknown")
        self.assertEqual(label_kind("Not Applicable"), "not_applicable")

    def test_blanks_and_coded_missing_are_separate(self):
        frame = pd.DataFrame({"X": ["", " ", "9", "0"],
                              "XNAME": ["", "", "Reported as Unknown", "None"]})
        missing, _, _ = audit_table(frame, "example", 2020)
        self.assertEqual(missing[0]["blank_rows"], 2)
        self.assertEqual(missing[0]["unknown_or_not_reported_rows"], 1)
        self.assertEqual(missing[1]["literal_none_rows"], 1)

    def test_changed_labels_and_within_year_conflicts(self):
        pairs = pd.DataFrame([
            {"year": 2020, "table": "vehicle", "column": "X", "code": "1", "label": "Old"},
            {"year": 2021, "table": "vehicle", "column": "X", "code": "1", "label": "New"},
            {"year": 2021, "table": "vehicle", "column": "X", "code": "1", "label": "Other"},
        ])
        result = coding_changes(pairs).iloc[0]
        self.assertTrue(result.label_changed)
        self.assertTrue(result.within_year_conflict)
        self.assertTrue(result.not_observed_every_year)


if __name__ == "__main__":
    unittest.main()

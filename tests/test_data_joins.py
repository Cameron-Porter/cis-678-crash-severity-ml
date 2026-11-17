"""Small cases for joins that could otherwise lose or multiply records."""

import unittest

import pandas as pd

from src.data.joins import audit_raw_joins, merge_crash_summary


class CrashJoinTests(unittest.TestCase):
    def setUp(self):
        # The same CASENUM in two years must stay separate.
        self.accident = pd.DataFrame({"YEAR_FILE": [2020, 2021], "CASENUM": [1, 1]})
        self.vehicle = self.accident.assign(VEH_NO=1)
        self.person = self.vehicle.assign(PER_NO=1)

    def test_year_keys_and_unmatched_crash_are_preserved(self):
        summary = self.accident.iloc[:1].assign(value=42)
        joined = merge_crash_summary(self.accident, summary)
        self.assertEqual(len(joined), 2)
        self.assertEqual(joined.loc[0, "value"], 42)
        self.assertTrue(pd.isna(joined.loc[1, "value"]))

    def test_duplicate_summary_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            merge_crash_summary(self.accident, pd.concat([self.accident] * 2))

    def test_unknown_summary_crash_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "absent"):
            merge_crash_summary(self.accident, self.accident.assign(CASENUM=99))

    def test_invalid_raw_keys_are_rejected(self):
        for table in ("accident", "vehicle", "person"):
            for invalid in ("duplicate", "missing"):
                with self.subTest(table=table, invalid=invalid):
                    tables = {name: getattr(self, name).copy() for name in ("accident", "vehicle", "person")}
                    if invalid == "duplicate":
                        tables[table] = pd.concat([tables[table]] * 2)
                    else:
                        tables[table].loc[0, "CASENUM"] = float("nan")
                    with self.assertRaises(ValueError):
                        audit_raw_joins(**tables)

    def test_orphan_child_crash_is_rejected(self):
        for table in ("vehicle", "person"):
            with self.subTest(table=table):
                tables = {name: getattr(self, name).copy() for name in ("accident", "vehicle", "person")}
                tables[table].loc[0, "CASENUM"] = 99
                with self.assertRaisesRegex(ValueError, "matching accident"):
                    audit_raw_joins(**tables)

    def test_missing_people_and_vehicle_links_are_reported(self):
        people = pd.DataFrame({"YEAR_FILE": [2020, 2020], "CASENUM": [1, 1],
                               "VEH_NO": [0, 9], "PER_NO": [1, 1]})
        report = audit_raw_joins(self.accident, self.vehicle, people).set_index("year")
        self.assertEqual(report.loc[2020, "people_with_vehicle_no_zero"], 1)
        self.assertEqual(report.loc[2020, "people_without_matching_vehicle"], 1)
        self.assertEqual(report.loc[2021, "crashes_without_people"], 1)
        self.assertEqual(report.person_rows.sum(), len(people))


if __name__ == "__main__":
    unittest.main()

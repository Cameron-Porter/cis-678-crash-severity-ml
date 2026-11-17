"""Severity boundaries, missing outcomes, and precedence."""

import unittest

import pandas as pd

from src.data.severity import classify_crashes, compare_training_labels, training_distribution


class SeverityTests(unittest.TestCase):
    def classify(self, injuries, vehicles):
        accident = pd.DataFrame({"YEAR_FILE": [2020], "CASENUM": [1]})
        person = pd.DataFrame([
            [2020, 1, 1, i + 1, value] for i, value in enumerate(injuries)
        ], columns=["YEAR_FILE", "CASENUM", "VEH_NO", "PER_NO", "INJ_SEV"])
        vehicle = pd.DataFrame([
            [2020, 1, i + 1, tow, damage] for i, (tow, damage) in enumerate(vehicles)
        ], columns=["YEAR_FILE", "CASENUM", "VEH_NO", "TOWED", "DEFORMED"])
        return classify_crashes(accident, vehicle, person).iloc[0]

    def test_high_overrides_other_outcomes(self):
        for injury in (3, 4):
            self.assertEqual(self.classify([9, injury], [(9, 9)]).SEVERITY, "high")
            self.assertEqual(self.classify([injury], []).SEVERITY, "high")

    def test_moderate_evidence(self):
        for injury in (1, 2):
            self.assertEqual(self.classify([injury, None], []).SEVERITY, "moderate")
        for tow in (2, 3, 6, 7):
            self.assertEqual(self.classify([9], [(tow, 9)]).SEVERITY, "moderate")
        self.assertEqual(self.classify([9], [(9, 6)]).SEVERITY, "moderate")

    def test_low_requires_every_outcome_known(self):
        for damage in (0, 2, 4):
            self.assertEqual(self.classify([0, 0], [(5, damage)]).SEVERITY, "low")
        self.assertEqual(self.classify([0], [(5, 0), (5, None)]).SEVERITY, "unknown")

    def test_unknown_codes_blanks_and_unexpected_codes(self):
        for injury in (5, 6, 9, None, pd.NA, 99):
            self.assertEqual(self.classify([0, injury], [(5, 0)]).SEVERITY, "unknown")
        for tow in (8, 9, None, pd.NA, 0, 99):
            self.assertEqual(self.classify([0], [(tow, 0)]).SEVERITY, "unknown")
        for damage in (7, 8, 9, None, pd.NA, 99):
            self.assertEqual(self.classify([0], [(5, damage)]).SEVERITY, "unknown")

    def test_missing_records(self):
        self.assertEqual(self.classify([], [(2, 6)]).SEVERITY_REASON, "no_person_records")
        self.assertEqual(self.classify([0], []).SEVERITY_REASON, "no_vehicle_records")
        self.assertEqual(self.classify([], []).SEVERITY, "unknown")

    def test_strongest_vehicle_and_person_are_used(self):
        self.assertEqual(self.classify([0, 2], [(5, 0), (2, 6)]).SEVERITY_REASON,
                         "minor_or_possible_injury")
        self.assertEqual(self.classify([0], [(5, 0), (5, 6)]).SEVERITY, "moderate")

    def test_training_report_rejects_holdout(self):
        labels = self.classify([0], [(5, 0)]).to_frame().T
        self.assertEqual(training_distribution(labels).rows.sum(), 1)
        for year in (2023, 2024):
            with self.assertRaisesRegex(ValueError, "training years"):
                training_distribution(labels.assign(YEAR_FILE=year))
            with self.assertRaisesRegex(ValueError, "training years"):
                compare_training_labels(labels.assign(YEAR_FILE=year))

    def test_injury_only_ignores_vehicle_outcomes(self):
        for vehicles in ([], [(2, 6)], [(9, 9)], [(5, 0)]):
            self.assertEqual(self.classify([0], vehicles).INJURY_ONLY_SEVERITY, "low")
            self.assertEqual(self.classify([0, 2], vehicles).INJURY_ONLY_SEVERITY, "moderate")
            self.assertEqual(self.classify([2, 4], vehicles).INJURY_ONLY_SEVERITY, "high")
            self.assertEqual(self.classify([0, None], vehicles).INJURY_ONLY_SEVERITY, "unknown")
            self.assertEqual(self.classify([], vehicles).INJURY_ONLY_SEVERITY, "unknown")

    def test_comparison_includes_unknowns_and_preserves_counts(self):
        labels = pd.DataFrame([
            self.classify([0], [(2, 6)]),   # moderate -> low
            self.classify([9], [(2, 6)]),   # moderate -> unknown
            self.classify([0], [(9, 9)]),   # unknown -> low
            self.classify([4], [(5, 0)]),   # high -> high
        ])
        labels["CASENUM"] = [1, 2, 3, 4]
        counts, comparison = compare_training_labels(labels)
        totals = counts.loc[counts.scope.eq("all_training")]
        self.assertEqual(totals.groupby("definition").rows.sum().to_dict(),
                         {"combined": 4, "injury_only": 4})
        cross = comparison.loc[comparison.scope.eq("all_training")]
        self.assertEqual(cross.rows.sum(), 4)
        self.assertEqual(cross.loc[cross.changed, "rows"].sum(), 3)
        self.assertEqual(cross.loc[cross.injury_only.eq("unknown"), "rows"].sum(), 1)


if __name__ == "__main__":
    unittest.main()

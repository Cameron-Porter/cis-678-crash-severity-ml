"""Fixed crash severity rules. Review and reporting use 2020–2022 only."""

from pathlib import Path

import pandas as pd

from src.data.joins import CRASH_KEY, audit_raw_joins, check_keys, merge_crash_summary
from src.data.load import read_raw_csv


def classify_crashes(accident, vehicle, person):
    """Return one label and reason per crash; never fit rules to input data."""
    audit_raw_joins(accident, vehicle, person)
    people = person[CRASH_KEY].copy()
    people["HIGH"] = person.INJ_SEV.isin([3, 4])
    people["MOD_INJ"] = person.INJ_SEV.isin([1, 2])
    people["ALL_NO_INJ"] = person.INJ_SEV.eq(0).fillna(False)
    people["PERSON_ROWS"] = 1
    people = people.groupby(CRASH_KEY).agg(
        HIGH=("HIGH", "any"), MOD_INJ=("MOD_INJ", "any"),
        ALL_NO_INJ=("ALL_NO_INJ", "all"), PERSON_ROWS=("PERSON_ROWS", "sum"),
    ).reset_index()

    vehicles = vehicle[CRASH_KEY].copy()
    vehicles["TOW"] = vehicle.TOWED.isin([2, 3, 6, 7])
    vehicles["DAMAGE"] = vehicle.DEFORMED.eq(6).fillna(False)
    # Positive lists prevent blanks and unexpected codes from becoming low.
    vehicles["ALL_NO_TOW"] = vehicle.TOWED.eq(5).fillna(False)
    vehicles["ALL_LOW_DAMAGE"] = vehicle.DEFORMED.isin([0, 2, 4])
    vehicles["VEHICLE_ROWS"] = 1
    vehicles = vehicles.groupby(CRASH_KEY).agg(
        TOW=("TOW", "any"), DAMAGE=("DAMAGE", "any"),
        ALL_NO_TOW=("ALL_NO_TOW", "all"),
        ALL_LOW_DAMAGE=("ALL_LOW_DAMAGE", "all"),
        VEHICLE_ROWS=("VEHICLE_ROWS", "sum"),
    ).reset_index()

    flags = merge_crash_summary(accident[CRASH_KEY], people)
    flags = merge_crash_summary(flags, vehicles)
    boolean_columns = ["HIGH", "MOD_INJ", "ALL_NO_INJ", "TOW", "DAMAGE",
                       "ALL_NO_TOW", "ALL_LOW_DAMAGE"]
    flags[boolean_columns] = flags[boolean_columns].astype("boolean").fillna(False)
    has_people = flags.PERSON_ROWS.fillna(0).gt(0)
    has_vehicles = flags.VEHICLE_ROWS.fillna(0).gt(0)
    result = flags[CRASH_KEY].copy()
    result["SEVERITY"] = "unknown"
    result["SEVERITY_REASON"] = "unresolved_outcomes"
    result.loc[~has_vehicles, "SEVERITY_REASON"] = "no_vehicle_records"
    result.loc[~has_people, "SEVERITY_REASON"] = "no_person_records"

    # Assign from lowest to highest precedence. Missing people stays unknown.
    rules = [
        (has_people & has_vehicles & flags.ALL_NO_INJ & flags.ALL_NO_TOW & flags.ALL_LOW_DAMAGE,
         "low", "known_low_outcomes"),
        (has_people & flags.DAMAGE, "moderate", "disabling_damage"),
        (has_people & flags.TOW, "moderate", "tow_away"),
        (has_people & flags.MOD_INJ, "moderate", "minor_or_possible_injury"),
        (flags.HIGH, "high", "serious_or_fatal_injury"),
    ]
    for mask, label, reason in rules:
        result.loc[mask, ["SEVERITY", "SEVERITY_REASON"]] = [label, reason]

    # Alternative target uses injuries only, including when vehicles are missing.
    result["INJURY_ONLY_SEVERITY"] = "unknown"
    result.loc[has_people & flags.ALL_NO_INJ, "INJURY_ONLY_SEVERITY"] = "low"
    result.loc[flags.MOD_INJ, "INJURY_ONLY_SEVERITY"] = "moderate"
    result.loc[flags.HIGH, "INJURY_ONLY_SEVERITY"] = "high"
    return result


def training_distribution(labels):
    """Count labels and reasons by training year; reject holdout rows."""
    if not labels.YEAR_FILE.isin([2020, 2021, 2022]).all():
        raise ValueError("Severity rule review is limited to training years 2020–2022")
    counts = labels.groupby(["YEAR_FILE", "SEVERITY", "SEVERITY_REASON"]).size().rename("rows").reset_index()
    counts["year_fraction"] = counts["rows"] / counts.groupby("YEAR_FILE")["rows"].transform("sum")
    return counts


def compare_training_labels(labels):
    """Compare targets on the same training crashes, keeping unknowns visible."""
    training_distribution(labels)  # Reject holdout years before computing reports.
    check_keys(labels, CRASH_KEY, "training labels")
    classes = ["low", "moderate", "high", "unknown"]
    columns = {"combined": "SEVERITY", "injury_only": "INJURY_ONLY_SEVERITY"}
    if not labels[list(columns.values())].isin(classes).all().all():
        raise ValueError("Both target definitions must have valid labels for every crash")
    cross_rows, class_rows = [], []
    groups = [(str(year), labels.loc[labels.YEAR_FILE.eq(year)]) for year in (2020, 2021, 2022)]
    groups.append(("all_training", labels))
    for scope, subset in groups:
        total = len(subset)
        for definition, column in columns.items():
            for label in classes:
                count = int(subset[column].eq(label).sum())
                class_rows.append({"scope": scope, "definition": definition, "label": label,
                                   "rows": count, "fraction": count / total if total else 0.0})
        for combined in classes:
            for injury in classes:
                count = int((subset.SEVERITY.eq(combined) & subset.INJURY_ONLY_SEVERITY.eq(injury)).sum())
                cross_rows.append({"scope": scope, "combined": combined, "injury_only": injury,
                                   "rows": count, "changed": combined != injury})
    return pd.DataFrame(class_rows), pd.DataFrame(cross_rows)


def write_training_reports(labels, directory):
    """Write counts, reasons, and target comparisons after the training-only check."""
    reasons = training_distribution(labels)
    counts, comparison = compare_training_labels(labels)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    reasons.to_csv(directory / "crss_severity_training.csv", index=False)
    counts.to_csv(directory / "crss_target_counts.csv", index=False)
    comparison.to_csv(directory / "crss_target_comparison.csv", index=False)


def main():
    root = Path(__file__).resolve().parents[2]
    columns = {
        "accident": ["CASENUM"],
        "vehicle": ["CASENUM", "VEH_NO", "TOWED", "DEFORMED"],
        "person": ["CASENUM", "VEH_NO", "PER_NO", "INJ_SEV"],
    }
    tables = {}
    for table, usecols in columns.items():
        tables[table] = pd.concat([
            read_raw_csv(root / "data" / "raw" / str(year) / f"{table}.csv",
                         usecols=usecols).assign(YEAR_FILE=year)
            for year in (2020, 2021, 2022)
        ], ignore_index=True)
    labels = classify_crashes(**tables)
    write_training_reports(labels, root / "docs")
    print(labels.SEVERITY.value_counts().to_string())
    print("Wrote training severity reports in docs/")


if __name__ == "__main__":
    main()

"""Report blanks, coded missing values, and observed code-label changes.

Run from the repository root: python -m src.data.audit_codes
All years are audited for compatibility. Reports do not fit preprocessing.
"""

from pathlib import Path

import pandas as pd

from src.data.load import read_raw_csv


YEARS = (2020, 2021, 2022, 2023, 2024)
TABLES = ("accident", "vehicle", "person")
# A different identifier appearing each year is not a category change.
IDENTIFIER_FIELDS = {"VIN", "TRLR1VIN", "TRLR2VIN", "DR_ZIP", "MCARR_ID", "MCARR_I2"}
# Reviewed against the 2016–2022 and 2016–2024 CRSS manuals.
# Do not use these numbers as a global missing-code list.
VALID_CODES = {
    ("accident", "WRK_ZONE"): {0, 1, 2, 3, 4},
    ("accident", "LGT_COND"): set(range(1, 10)),
    ("accident", "WEATHER"): {1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 98, 99},
    ("vehicle", "TOWED"): {2, 3, 5, 6, 7, 8, 9},
    ("vehicle", "DEFORMED"): {0, 2, 4, 6, 7, 8, 9},
    ("person", "INJ_SEV"): {0, 1, 2, 3, 4, 5, 6, 9},
}


def blank_mask(values):
    return values.isna() | values.astype("string").str.strip().eq("").fillna(False)


def label_kind(label):
    """Flag label wording for review; never recode a value based on this text."""
    value = str(label).strip().lower()
    if value in {"unknown", "reported as unknown", "unknown/not reported", "not reported"}:
        return "unknown_or_not_reported"
    if "not applicable" in value:
        return "not_applicable"
    if "unknown" in value:
        return "partly_unknown"
    return "other"


def validate_codes(frame, table, year):
    """Check the reviewed fields against the codes allowed in that year."""
    checks = []
    if year not in YEARS:
        raise ValueError(f"Unreviewed year: {year}")
    for (rule_table, column), valid in VALID_CODES.items():
        if table != rule_table:
            continue
        if column not in frame:
            raise ValueError(f"{year} {table}: required reviewed field {column} is absent")
        if column == "TOWED":
            valid = {2, 3, 5, 7, 8, 9} if year < 2022 else {5, 6, 8, 9}
        elif column == "DEFORMED" and year < 2022:
            valid = valid - {7}
        values = frame[column]
        invalid = ~blank_mask(values) & ~pd.to_numeric(values, errors="coerce").isin(valid)
        checks.append({"year": year, "table": table, "column": column,
                       "check": "outside_reviewed_code_set", "rows": int(invalid.sum())})
    return checks


def audit_table(frame, table, year):
    """Return per-field missingness, observed code labels, and validation results."""
    missing, pairs, checks = [], [], []
    for column in frame:
        values = frame[column]
        blanks = blank_mask(values)
        record = {"year": year, "table": table, "column": column,
                  "rows": len(frame), "column_present": True,
                  "blank_rows": int(blanks.sum()),
                  "blank_fraction": float(blanks.mean()) if len(frame) else 0.0,
                  "literal_none_rows": int(values.eq("None").fillna(False).sum()),
                  "unknown_or_not_reported_rows": None,
                  "partly_unknown_rows": None, "not_applicable_rows": None}
        name_column = column + "NAME"
        if name_column in frame:
            labels = frame[name_column]
            kinds = labels.map({label: label_kind(label) for label in labels.dropna().unique()})
            for kind in ("unknown_or_not_reported", "partly_unknown", "not_applicable"):
                record[kind + "_rows"] = int((~blanks & kinds.eq(kind)).sum())
            observed = pd.DataFrame({"code": values, "label": labels}).fillna("")
            for (code, label), count in observed.value_counts(sort=False).items():
                pairs.append({"year": year, "table": table, "column": column,
                              "code": code, "label": label, "rows": int(count),
                              "label_kind": label_kind(label)})
            checks.append({"year": year, "table": table, "column": column,
                           "check": "code_without_label", "rows": int((~blanks & blank_mask(labels)).sum())})
        missing.append(record)

    checks.extend(validate_codes(frame, table, year))
    return missing, pairs, checks


def coding_changes(pairs):
    """Flag changed text, within-year conflicts, and codes absent in some years."""
    keys = ["table", "column", "code"]
    observed = pairs.loc[
        pairs.code.astype("string").str.strip().ne("") &
        pairs.label.astype("string").str.strip().ne(""),
        keys + ["year", "label"],
    ].drop_duplicates().sort_values(keys + ["year", "label"])
    grouped = observed.groupby(keys, dropna=False)
    summary = grouped.agg(label_count=("label", "nunique"), year_count=("year", "nunique"))
    per_year = observed.groupby(keys + ["year"], dropna=False).label.agg(["nunique", " | ".join])
    summary["within_year_conflict"] = per_year["nunique"].groupby(level=keys).max().gt(1)
    summary["label_changed"] = summary.label_count.gt(1)
    summary["not_observed_every_year"] = summary.year_count.ne(len(YEARS))
    text = per_year["join"].unstack("year").reindex(columns=YEARS).fillna("")
    text.columns = [f"labels_{year}" for year in YEARS]
    summary = summary.join(text)
    category_absence = summary.not_observed_every_year & ~summary.index.get_level_values("column").isin(IDENTIFIER_FIELDS)
    summary = summary.loc[summary.label_changed | summary.within_year_conflict | category_absence]
    return summary.drop(columns=["label_count", "year_count"]).reset_index()


def main():
    root = Path(__file__).resolve().parents[2]
    missing, pairs, checks = [], [], []
    for year in YEARS:
        for table in TABLES:
            frame = read_raw_csv(root / "data" / "raw" / str(year) / f"{table}.csv", text=True)
            m, p, c = audit_table(frame, table, year)
            missing.extend(m)
            pairs.extend(p)
            checks.extend(c)
        print(f"Audited {year}", flush=True)
    # An absent column is structural absence, not a column full of observed blanks.
    for table in TABLES:
        fields = {r["column"] for r in missing if r["table"] == table}
        for year in YEARS:
            present = [r for r in missing if r["table"] == table and r["year"] == year]
            for column in sorted(fields - {r["column"] for r in present}):
                missing.append({"year": year, "table": table, "column": column,
                                "rows": present[0]["rows"], "column_present": False})
    missing_frame = pd.DataFrame(missing).sort_values(["year", "table", "column"])
    pair_frame = pd.DataFrame(pairs)
    changes = coding_changes(pair_frame)
    checks_frame = pd.DataFrame(checks).sort_values(["year", "table", "column", "check"])
    # Only retain noteworthy label categories, not every vehicle make/model name.
    special = pair_frame.loc[pair_frame.label_kind.ne("other")].sort_values(["year", "table", "column", "code"])
    reports = {"crss_missingness.csv": missing_frame, "crss_special_codes.csv": special,
               "crss_coding_changes.csv": changes, "crss_code_checks.csv": checks_frame}
    for filename, report in reports.items():
        report.to_csv(root / "docs" / filename, index=False)
    violations = checks_frame.loc[checks_frame.check.eq("outside_reviewed_code_set"), "rows"].sum()
    if violations:
        raise ValueError(f"{violations} values outside reviewed code sets; inspect docs/crss_code_checks.csv")
    print("Wrote four audit reports in docs/; reviewed code sets passed.")


if __name__ == "__main__":
    main()

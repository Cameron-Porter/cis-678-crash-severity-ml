"""Rebuild crash-level preparation tables with fixed chronological splits."""

import hashlib
import json
import platform
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from src.data.audit_codes import TABLES, YEARS, validate_codes
from src.data.joins import CRASH_KEY, audit_raw_joins, check_keys, merge_crash_summary
from src.data.load import read_raw_csv
from src.data.severity import classify_crashes, write_training_reports

SPLIT_YEARS = {"train": (2020, 2021, 2022), "validation": (2023,), "test": (2024,)}
DROP_COLUMNS = ["MAX_SEV", "MAX_SEVNAME", "NUM_INJ", "NUM_INJNAME", "MAXSEV_IM",
                "MAXSEV_IMNAME", "NO_INJ_IM", "NO_INJ_IMNAME", "STRATUM", "STRATUMNAME", "PSUSTRAT"]
# Fixed output contract. Adding a raw column must not silently add a predictor.
OUTPUT_COLUMNS = """CASENUM REGION REGIONNAME PSU PJ PSU_VAR URBANICITY URBANICITYNAME
VE_TOTAL VE_FORMS PVH_INVL PEDS PERMVIT PERNOTMVIT MONTH MONTHNAME YEAR YEARNAME
DAY_WEEK DAY_WEEKNAME HOUR HOURNAME MINUTE MINUTENAME HARM_EV HARM_EVNAME ALCOHOL
ALCOHOLNAME MAN_COLL MAN_COLLNAME RELJCT1 RELJCT1NAME RELJCT2 RELJCT2NAME TYP_INT
TYP_INTNAME WRK_ZONE WRK_ZONENAME REL_ROAD REL_ROADNAME LGT_COND LGT_CONDNAME SCH_BUS
SCH_BUSNAME INT_HWY INT_HWYNAME WEATHER WEATHERNAME WKDY_IM WKDY_IMNAME HOUR_IM
HOUR_IMNAME MINUTE_IM MINUTE_IMNAME EVENT1_IM EVENT1_IMNAME MANCOL_IM MANCOL_IMNAME
RELJCT1_IM RELJCT1_IMNAME RELJCT2_IM RELJCT2_IMNAME LGTCON_IM LGTCON_IMNAME WEATHR_IM
WEATHR_IMNAME ALCHL_IM ALCHL_IMNAME WEIGHT YEAR_FILE SEVERITY""".split()


def notebook_root():
    """Require the repository's notebooks directory for either entry point."""
    root = Path(__file__).resolve().parents[2]
    if Path.cwd().resolve() != root / "notebooks":
        raise RuntimeError("Run preprocessing from this repository's notebooks/ directory.")
    return root


def load_tables(root):
    tables = {}
    for table in TABLES:
        frames = []
        for year in YEARS:
            frame = read_raw_csv(root / "data/raw" / str(year) / f"{table}.csv")
            if any(check["rows"] for check in validate_codes(frame, table, year)):
                raise ValueError(f"{year} {table}: values outside reviewed code sets")
            if "YEAR_FILE" in frame:
                raise ValueError("Raw data must not contain generated YEAR_FILE")
            frames.append(frame.assign(YEAR_FILE=year))
        tables[table] = pd.concat(frames, ignore_index=True)
    return tables


def split_crashes(crashes):
    splits = {name: crashes.loc[crashes.YEAR_FILE.isin(years)].sort_values(CRASH_KEY).reset_index(drop=True)
              for name, years in SPLIT_YEARS.items()}
    validate_splits(splits, crashes)
    return splits


def validate_splits(splits, crashes):
    """Reject omitted crashes, overlapping keys, wrong years, or changed values."""
    if set(splits) != set(SPLIT_YEARS):
        raise ValueError("Expected train, validation, and test splits")
    check_keys(crashes, CRASH_KEY, "complete crash table")
    for name, years in SPLIT_YEARS.items():
        frame = splits[name]
        if list(frame.columns) != OUTPUT_COLUMNS:
            raise ValueError(f"{name}: processed schema changed")
        check_keys(frame, CRASH_KEY, name)
        if set(frame.YEAR_FILE.unique()) != set(years):
            raise ValueError(f"{name}: incorrect or missing years")
        if not frame.YEAR.eq(frame.YEAR_FILE).all():
            raise ValueError(f"{name}: YEAR differs from source folder")
        if not frame.SEVERITY.isin(["low", "moderate", "high", "unknown"]).all():
            raise ValueError(f"{name}: missing or invalid severity")
    combined = pd.concat(splits.values(), ignore_index=True)
    check_keys(combined, CRASH_KEY, "combined splits")
    expected = crashes.sort_values(CRASH_KEY).reset_index(drop=True)
    actual = combined.sort_values(CRASH_KEY).reset_index(drop=True)
    pd.testing.assert_frame_equal(actual, expected, check_dtype=False, check_exact=True)


def processed_schema(crashes):
    rows = []
    for column in OUTPUT_COLUMNS:
        dtype = "string" if pd.api.types.is_string_dtype(crashes[column]) else str(crashes[column].dtype)
        if column in CRASH_KEY:
            role, rule = "key", "Combine YEAR_FILE and CASENUM; never a predictor"
        elif column == "SEVERITY":
            role, rule = "target", "low/moderate/high/unknown; exclude unknown for modeling"
        elif column == "WEIGHT":
            role, rule = "sample_weight", "Use only if the analysis calls for survey weighting"
        elif column in {"PSU", "PJ", "PSU_VAR", "YEAR", "YEARNAME"}:
            role, rule = "metadata", "Survey or year metadata; not a predictor"
        elif column.endswith("NAME"):
            role, rule = "code_label", "Text label for corresponding code; preserve literal None"
        else:
            role, rule = "pending_review", "Retained source field; availability and leakage review required before modeling"
        rows.append({"column": column, "dtype": dtype, "source": "derived" if column in {"YEAR_FILE", "SEVERITY"} else "accident",
                     "role": role, "handling": rule})
    return pd.DataFrame(rows)


def read_processed_csv(path, schema):
    """Read UTF-8 outputs using the schema, preserving valid literal text."""
    return pd.read_csv(path, encoding="utf-8", keep_default_na=False, na_values=[""],
                       dtype=dict(zip(schema.column, schema.dtype)), float_precision="round_trip")


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def input_hashes(root):
    """Record the raw files before loading and check them again before saving."""
    root = Path(root)
    inputs = [root / "data/raw" / str(year) / f"{table}.csv" for year in YEARS for table in TABLES]
    return {p.relative_to(root).as_posix(): sha256(p) for p in inputs}


def prepare_crashes(accident, labels):
    """Attach the primary target and remove the fixed excluded columns."""
    crashes = merge_crash_summary(accident, labels[CRASH_KEY + ["SEVERITY"]])
    return crashes.drop(columns=DROP_COLUMNS).sort_values(CRASH_KEY).reset_index(drop=True)


def save_datasets(root, splits, crashes, labels, audit, raw_hashes):
    """Check prepared splits and saved contents before replacing local outputs."""
    root = Path(root)
    validate_splits(splits, crashes)
    schema = processed_schema(crashes)
    out = root / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=out, prefix="build-") as temporary:
        staging = Path(temporary)
        for name, frame in splits.items():
            frame.to_csv(staging / f"{name}.csv", index=False, encoding="utf-8", lineterminator="\n")
        reloaded = {name: read_processed_csv(staging / f"{name}.csv", schema) for name in splits}
        validate_splits(reloaded, crashes)
        if raw_hashes != input_hashes(root):
            raise ValueError("Raw inputs changed during the build")
        sources = sorted((root / "src/data").glob("*.py")) + [root / "notebooks/build_data.py"]
        manifest = {"python": platform.python_version(), "pandas": pd.__version__,
                    "inputs": raw_hashes,
                    "code": {p.relative_to(root).as_posix(): sha256(p) for p in sources},
                    "outputs": {f"{name}.csv": {"rows": len(frame), "columns": len(frame.columns),
                                "years": list(SPLIT_YEARS[name]), "sha256": sha256(staging / f"{name}.csv")}
                                for name, frame in splits.items()}}
        for name in splits:
            (staging / f"{name}.csv").replace(out / f"{name}.csv")
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    schema.to_csv(docs / "crss_processed_schema.csv", index=False, lineterminator="\n")
    pd.DataFrame([{"split": name, "years": ";".join(map(str, SPLIT_YEARS[name])),
                   "rows": len(frame), "columns": len(frame.columns), "integrity": "passed"}
                  for name, frame in splits.items()]).to_csv(docs / "crss_processed_checks.csv", index=False, lineterminator="\n")
    audit = audit.copy()
    audit["joined_crash_rows"] = audit.year.map(crashes.groupby("YEAR_FILE").size())
    audit.to_csv(docs / "crss_join_audit.csv", index=False)
    write_training_reports(labels.loc[labels.YEAR_FILE.isin(SPLIT_YEARS["train"])], docs)


def build_datasets(root):
    """Run the same steps exposed individually in the preprocessing notebook."""
    raw_hashes = input_hashes(root)
    tables = load_tables(root)
    audit = audit_raw_joins(**tables)
    labels = classify_crashes(**tables)
    crashes = prepare_crashes(tables["accident"], labels)
    splits = split_crashes(crashes)
    save_datasets(root, splits, crashes, labels, audit, raw_hashes)
    return splits

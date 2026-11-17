"""Build the inventory and schema report from data/raw/<YEAR>/.

Reads local CSVs only. Does not download data or use the processed splits.
Leaves the raw files unchanged.

Run from the repository root: python src/data/document_raw.py
Uses only the Python standard library.
"""

import csv
import hashlib
from pathlib import Path


YEARS = range(2020, 2025)
TABLES = (
    "accident cevent crashrf damage distract drimpair driverrf factor maneuver "
    "nmcrash nmdistract nmimpair nmprior parkwork pbtype person personrf "
    "pvehiclesf safetyeq vehicle vehiclesf vevent violatn vision vpicdecode "
    "vpictrailerdecode vsoe weather"
).split()


def main():
    root = Path(__file__).resolve().parents[2]
    records = []
    schemas = {}
    for year in YEARS:
        folder = root / "data" / "raw" / str(year)
        files = {p.name.lower(): p for p in folder.glob("*.csv")}
        expected = {f"{table}.csv" for table in TABLES}
        if set(files) != expected or len(list(folder.glob("*.csv"))) != len(expected):
            raise ValueError(
                f"{folder}: missing={sorted(expected - set(files))}, "
                f"unexpected={sorted(set(files) - expected)}; "
                "expected exactly 28 CSVs directly in the year folder"
            )
        for table in TABLES:
            path = files[f"{table}.csv"]
            with path.open("rb") as stream:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            with path.open(encoding="latin-1", newline="") as stream:
                reader = csv.reader(stream)
                header = next(reader)
                if len(header) != len(set(header)):
                    raise ValueError(f"Duplicate column names: {path}")
                rows = 0
                for row in reader:
                    if len(row) != len(header):
                        raise ValueError(f"Incorrect column count: {path}, record {rows + 2}")
                    rows += 1
            schemas[year, table] = header
            records.append({
                "year": year, "table": f"{table}.csv", "rows": rows,
                "columns": len(header), "bytes": path.stat().st_size,
                "sha256": digest,
                "source_url": f"https://static.nhtsa.gov/nhtsa/downloads/CRSS/{year}/CRSS{year}CSV.zip",
            })
        print(f"Documented {year}: {len(files)} tables", flush=True)

    docs = root / "docs"
    docs.mkdir(exist_ok=True)
    with (docs / "crss_inventory.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    lines = [
        "# CRSS raw CSV schemas, 2020–2024", "",
        "Built from our local `data/raw/<YEAR>/` files using `python src/data/document_raw.py`.",
        "The script does not download data or read the processed splits.",
        "See [data/README.md](../data/README.md) for sources, keys, and setup.", "",
        "The [inventory](crss_inventory.csv) lists row counts, column counts, sizes, hashes,",
        "and source URLs. We calculate the hashes from our local files so teammates can",
        "compare copies. NHTSA did not supply these hashes.", "",
        "Each section starts with the 2020 columns in file order, then lists changes from",
        "the previous year. Added columns use the new year's order; removed columns use",
        "the previous year's order. Order checks compare columns present in both years.", "",
        "This report checks columns. We will review code meanings and missing codes in",
        "DATA-04. CSV files do not specify data types; use the NHTSA manuals linked in",
        "the README to check what each field and code means.", "",
        "## Core table sizes", "",
        "| Year | Table | Rows | Columns |", "|---|---|---:|---:|",
    ]
    for record in records:
        if record["table"] in {"accident.csv", "vehicle.csv", "person.csv"}:
            lines.append(f'| {record["year"]} | {record["table"]} | {record["rows"]:,} | {record["columns"]} |')
    for table in TABLES:
        lines.extend(["", f"## {table}.csv", "", "2020 columns:", "", "```text",
                      ", ".join(schemas[2020, table]), "```", "",
                      "| Year | Added columns | Removed columns | Shared column order changed? |",
                      "|---|---|---|---|"])
        for year in range(2021, 2025):
            previous, current = schemas[year - 1, table], schemas[year, table]
            added = ", ".join(f"`{c}`" for c in current if c not in previous) or "None"
            removed = ", ".join(f"`{c}`" for c in previous if c not in current) or "None"
            changed = [c for c in previous if c in current] != [c for c in current if c in previous]
            lines.append(f'| {year} | {added} | {removed} | {"Yes" if changed else "No"} |')
    (docs / "crss_schema.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote docs/crss_inventory.csv and docs/crss_schema.md")


if __name__ == "__main__":
    main()

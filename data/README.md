# Data

This folder holds the NHTSA Crash Report Sampling System (CRSS) data used by the project. Data files are **not** committed to git (see `.gitignore`); each team member downloads them locally.

## Layout

```text
data/
├── raw/                 # Original CRSS CSV files, one folder per year (unmodified)
│   ├── 2020/            # Training
│   ├── 2021/            # Training
│   ├── 2022/            # Training
│   ├── 2023/            # Validation
│   └── 2024/            # Test (do not use for preprocessing/feature/model decisions)
└── processed/           # Cleaned, merged, and labeled datasets produced by src/data/
```

Each year folder contains the 28 CRSS CSV tables (e.g. `accident.csv`, `vehicle.csv`, `person.csv`, `weather.csv`, ...). Key tables:

| File | Level | Notes |
|---|---|---|
| `accident.csv` | One row per crash | Within-year key: `CASENUM`; roadway/environmental fields |
| `vehicle.csv` | One row per vehicle | Within-year key: `CASENUM`, `VEH_NO`; vehicle, towing, and damage fields |
| `person.csv` | One row per person | Within-year key: `CASENUM`, `VEH_NO`, `PER_NO`; person and injury fields |

When combining years, add `YEAR_FILE` using the year folder and include it in
each key above. We add this column during preprocessing. Leave the raw files
as downloaded.

## Schemas and supplementary tables

These reports use our downloaded files in `data/raw/<YEAR>/`:

- [Schemas](../docs/crss_schema.md): column names and yearly changes for all 28 tables.
- [Inventory](../docs/crss_inventory.csv): row counts, column counts, sizes, SHA-256 hashes, and source URLs for all 140 CSVs.

The script reads local files only. It does not download from NHTSA or read our
processed train, validation, and test tables. Source URLs show where the raw
data came from. Hashes let us check that everyone has the same file contents,
even if NHTSA later updates the downloads.

CSV files do not specify data types. Use IDs as keys, code fields as categories,
`*NAME` fields as text labels, and `WEIGHT` as a survey weight. A numeric code
does not make a field a numeric measurement. The NHTSA manuals below explain
the fields and codes. We will review missing codes and consistency in DATA-04.

The download includes the supplementary tables bundled in each main CSV archive:

| Tables | Contents / potential use |
|---|---|
| `weather` | Additional crash weather records |
| `cevent`, `vevent`, `vsoe`, `damage` | Crash/vehicle events and damage records |
| `crashrf`, `driverrf`, `personrf`, `vehiclesf`, `pvehiclesf` | Related factors and circumstances |
| `distract`, `drimpair`, `factor`, `maneuver`, `violatn`, `vision` | Driver/vehicle circumstances |
| `nmcrash`, `nmdistract`, `nmimpair`, `nmprior`, `pbtype`, `safetyeq` | Nonmotorist circumstances, crash typing, and safety equipment |
| `parkwork` | Parked/working vehicle records |
| `vpicdecode`, `vpictrailerdecode` | Decoded vehicle and trailer information |

The notebook currently uses `accident`, `vehicle`, and `person`. The other tables
can have multiple rows per crash, vehicle, or person. Check their columns and
the manual before joining them. We do not currently use or download NHTSA's
separate **AuxiliaryCSV** archives.

After downloading all five years, run this from the repository root to update
both reports:

```bash
python src/data/document_raw.py
```

On macOS, use `python3` in place of `python`. The script checks that all 28 tables
are present for each year and that each row has the expected number of columns.
It leaves the data unchanged. We will check duplicate keys and join coverage
in DATA-02.

### Changes by year

These are the column changes in our downloaded files. The schema report also
lists changes in the other tables.

| Year | Core-table changes from the previous year |
|---|---|
| 2020 | Baseline: accident has 80 columns, vehicle 167, and person 108. |
| 2021 | Core-table column order changes. Vehicle drops `BDYTYP_IM` / `BDYTYP_IMNAME`, adds `UNDEROVERRIDE` / `UNDEROVERRIDENAME`, and changes `V_Config` / `V_ConfigNAME` to uppercase. |
| 2022 | Person adds `DEVMOTOR`, `DEVMOTORNAME`, `DEVTYPE`, and `DEVTYPENAME` (112 columns). Vehicle returns to mixed-case `V_Config` / `V_ConfigNAME`. |
| 2023 | Vehicle adds `ACC_CONFIG` / `ACC_CONFIGNAME` (169 columns). |
| 2024 | Vehicle removes `ACC_CONFIG` / `ACC_CONFIGNAME` (167 columns) and returns to uppercase `V_CONFIG` / `V_CONFIGNAME`. |

Accident column names stay the same across all five years. Load columns by name,
not position. The notebook makes column names uppercase before combining years,
so `V_Config` and `V_CONFIG` match. A missing column does not mean its values
were zero. We still need to check whether codes changed, even when column names
stayed the same (DATA-04).

## Source

Downloaded from NHTSA (CSV format):

```text
https://static.nhtsa.gov/nhtsa/downloads/CRSS/<YEAR>/CRSS<YEAR>CSV.zip
```

- [CRSS overview](https://www.nhtsa.gov/crash-data-systems/crash-report-sampling-system)
- [NHTSA CRSS download directory](https://www.nhtsa.gov/file-downloads?p=nhtsa%2Fdownloads%2FCRSS%2F): year folders contain archives and release notes.
- [Official CRSS manuals index](https://static.nhtsa.gov/nhtsa/downloads/CRSS/Links%20for%20CRSS%20Manuals.pdf): links to the Analytical User's Manual and coding manuals.
- [2024 FARS/CRSS Coding and Validation Manual](https://crashstats.nhtsa.dot.gov/Api/Public/ViewPublication/813798): detailed coding definitions; consult the relevant year's documentation when interpreting earlier data.

Crash counts (rows in `accident.csv`): 2020: 54,745 · 2021: 54,200 · 2022: 53,955 · 2023: 50,103 · 2024: 51,658.

## Downloading the data

From the **repository root**, paste the entire command for your operating system.
Python 3 is required; no additional packages are needed. Each command downloads
2020–2024, creates the year folders, and extracts CSV files directly into them.

### macOS (Terminal)

```bash
python3 -c '
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile
import shutil

assert Path("data/README.md").is_file(), "Run from the repository root."
for year in range(2020, 2025):
    folder = Path("data/raw") / str(year)
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / f"CRSS{year}CSV.zip"
    print(f"Downloading {year}...", flush=True)
    urlretrieve(f"https://static.nhtsa.gov/nhtsa/downloads/CRSS/{year}/CRSS{year}CSV.zip", archive)
    with ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            name = Path(entry.filename).name.lower()
            if not entry.is_dir() and name.endswith(".csv"):
                with zipped.open(entry) as source, (folder / name).open("wb") as target:
                    shutil.copyfileobj(source, target)
    for name in ("accident.csv", "vehicle.csv", "person.csv"):
        if not (folder / name).is_file():
            raise FileNotFoundError(folder / name)
    archive.unlink()
    print(f"Ready: {folder}", flush=True)
'
```

### Windows (PowerShell)

```powershell
@'
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile
import shutil

assert Path("data/README.md").is_file(), "Run from the repository root."
for year in range(2020, 2025):
    folder = Path("data/raw") / str(year)
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / f"CRSS{year}CSV.zip"
    print(f"Downloading {year}...", flush=True)
    urlretrieve(f"https://static.nhtsa.gov/nhtsa/downloads/CRSS/{year}/CRSS{year}CSV.zip", archive)
    with ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            name = Path(entry.filename).name.lower()
            if not entry.is_dir() and name.endswith(".csv"):
                with zipped.open(entry) as source, (folder / name).open("wb") as target:
                    shutil.copyfileobj(source, target)
    for name in ("accident.csv", "vehicle.csv", "person.csv"):
        if not (folder / name).is_file():
            raise FileNotFoundError(folder / name)
    archive.unlink()
    print(f"Ready: {folder}", flush=True)
'@ | python -
```

Both commands normalize filenames to lowercase, including the 2020 archive's
`vpicTrailerDecode.csv`. Read files with an explicit encoding
(e.g. `encoding="latin-1"`) if pandas reports decode errors.

## Running preprocessing

Open [`notebooks/Data Preprocessing.ipynb`](../notebooks/Data%20Preprocessing.ipynb)
and run the cells in order. The working directory must be the repository's
`notebooks/` directory. Running from the repository root is not supported;
the setup cell raises an error if the working directory is incorrect.

The notebook reads `accident.csv`, `vehicle.csv`, and `person.csv` from
`data/raw/<YEAR>/` for 2020–2024. It writes `train.csv`, `validation.csv`, and
`test.csv` to `data/processed/`. No personal download paths need to be edited.

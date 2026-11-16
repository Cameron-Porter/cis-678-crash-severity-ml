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
| `accident.csv` | One row per crash | Crash-level roadway/environmental fields; join key `CASENUM` |
| `vehicle.csv` | One row per vehicle | Join on `CASENUM`, `VEH_NO` |
| `person.csv` | One row per person | Join on `CASENUM`, `VEH_NO`, `PER_NO`; contains injury severity |

Use the CRSS Analytical User's Manual for the meaning of each field and code.

## Source

Downloaded from NHTSA (CSV format):

```text
https://static.nhtsa.gov/nhtsa/downloads/CRSS/<YEAR>/CRSS<YEAR>CSV.zip
```

Crash counts (rows in `accident.csv`): 2020: 54,745 · 2021: 54,200 · 2022: 53,955 · 2023: 50,103 · 2024: 51,658.

## Re-downloading

From the repository root (Git Bash / macOS / Linux):

```bash
for y in 2020 2021 2022 2023 2024; do
  curl -sSfL -o "data/raw/CRSS${y}CSV.zip" "https://static.nhtsa.gov/nhtsa/downloads/CRSS/$y/CRSS${y}CSV.zip"
  unzip -q -o -j "data/raw/CRSS${y}CSV.zip" -d "data/raw/$y" && rm "data/raw/CRSS${y}CSV.zip"
done
```

Note: the 2020 archive names one file `vpicTrailerDecode.csv`; it was renamed to lowercase `vpictrailerdecode.csv` to match the other years. Read files with an explicit encoding (e.g. `encoding="latin-1"`) if pandas reports decode errors.

Total size is about 3.4 GB uncompressed.

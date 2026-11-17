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

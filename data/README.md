# Data

Download CRSS files locally into `data/raw/<YEAR>/` for 2020-2024. CSVs must sit
directly in each year folder. Raw data, processed datasets, and fitted artifacts
are excluded from git.

## Source

[NHTSA CRSS downloads](https://www.nhtsa.gov/file-downloads?p=nhtsa%2Fdownloads%2FCRSS%2F)
provide the yearly archives. Use the [2016-2022 manual](https://rosap.ntl.bts.gov/view/dot/78235/dot_78235_DS1.pdf)
and [2016-2024 manual](https://rosap.ntl.bts.gov/view/dot/89796/dot_89796_DS1.pdf)
for field definitions and year-specific codes.

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

Install the root `requirements.txt`, then run from the repository root:

```bash
cd notebooks
python build_data.py
python prepare_features.py
```

Use `python3` on macOS. Both commands require `notebooks/` as the working
directory. For individual steps, use [Data Preprocessing.ipynb](../notebooks/Data%20Preprocessing.ipynb)
and [Feature Preprocessing.ipynb](../notebooks/Feature%20Preprocessing.ipynb).
They call the same shared functions as the commands.

### Rebuilding the datasets

`build_data.py` checks inputs, labels each crash, and replaces these local files:

| File in `data/processed/` | Years | Rows |
|---|---|---:|
| `train.csv` | 2020-2022 | 162,900 |
| `validation.csv` | 2023 | 50,103 |
| `test.csv` | 2024 | 51,658 |

Each has 71 columns, sorted by `YEAR_FILE`, `CASENUM`. The
[processed schema](../docs/crss_processed_schema.csv) describes column roles;
these tables are not an approved model input matrix. `manifest.json` records
input, code, and output hashes and library versions. Saved CSVs are reloaded
and checked before replacement. Read them with `read_processed_csv` from
`src/data/preprocess.py` to preserve valid text such as `None`.

## Crash-level joins

Use `YEAR_FILE` with `CASENUM` as the crash key; add `VEH_NO` for vehicles and
`PER_NO` for people. Group vehicle/person records before joining to crashes.
Missing or duplicate keys and records without a parent crash fail validation.
One-to-one joins preserve every crash. People without matching vehicle records
are reported and retained in crash summaries; `VEH_NO=0` has no vehicle link.

## Crash severity rules

Apply these fixed rules in order using all people and vehicles in a crash:

| Label | Rule |
|---|---|
| High | Any `INJ_SEV` is 3 or 4. |
| Moderate | No known high injury, at least one person, and any `INJ_SEV` is 1 or 2, `TOWED` is 2, 3, 6, or 7, or `DEFORMED` is 6. |
| Low | At least one person and vehicle; every injury is 0, every tow code is 5, and every damage code is 0, 2, or 4. |
| Unknown | No person records or insufficient evidence for the other labels. |

Known high or moderate evidence takes precedence over unresolved outcomes.
Blanks and unknown codes never establish low severity. Injury codes 5, 6, and 9
are unresolved; code 6 is death before the crash, not a crash fatality.
Keep unknown labels in processed files and exclude them before modeling,
reporting exclusions. Reasons and component outcomes are never predictors.

Moderate combines injury and vehicle disruption as the proposal's measure of
crash consequences, not a clinical injury scale. Towing without disabling damage
still qualifies. Because these outcomes are not equivalent, compare the primary
target with injury-only severity: high for injury 3/4, moderate for 1/2, low only
when all injuries are 0, otherwise unknown.

### Training comparison

On 162,900 training crashes, 43,548 (26.7%) change labels under the injury-only
definition. See [counts](../docs/crss_target_counts.csv) and the
[comparison](../docs/crss_target_comparison.csv); pooled `all_training` rows
must not be added to individual years. The primary target leaves 142,702 eligible
training crashes; 140,373 have known labels under both definitions.

Use matching predictors, splits, and tuning budgets for both definitions.
Compare on the shared eligible population and report each target's full eligible
population separately. Higher scores alone do not establish a better target.
Earlier notebook work viewed all five years; current rule-review reports use
training only, but that earlier holdout exposure cannot be undone.

## Missing values and coding consistency

Keep literal `None` work-zone labels; only empty CSV cells become null during
loading. The audit also counts whitespace-only cells as blank. Never replace
8/9/98/99 globally: codes are field-specific. Preserve partially known categories
and distinguish missing columns from observed blank values.

The loader checks `WRK_ZONE`, `LGT_COND`, `WEATHER`, `TOWED`, `DEFORMED`, and
`INJ_SEV`. Towing codes change in 2022: 2/3/7 are replaced by 6; damage code 7
is added. Column names are normalized to uppercase; collisions fail loading.
Other fields require review before use. Special-code and changed-label reports
are review flags, not instructions to automatically recode values. Identifier
absence-only flags are omitted from the coding report.

## Core and expanded feature sets

The [feature catalog](../docs/crss_feature_sets.csv) is the detailed reference
for sources, construction, missing codes, rationale, and availability.

| Set | Features |
|---|---|
| Core categorical | `MONTH`, `DAY_WEEK`, `HOUR`, `TYP_INT`, `INT_HWY`, `LGT_COND`, `WEATHER` |
| Core numeric | `VE_TOTAL`, `VEHICLE_AGE_MIN`, `VEHICLE_AGE_MAX` |
| Expanded additions | `SPEEDING_ANY`, `DRINKING_ANY` (categorical); `DRIVER_AGE_MIN`, `DRIVER_AGE_MAX` (numeric) |

The core set captures time, roadway, environment, and vehicle context. The
expanded set tests the contribution of driver age and reported behavior.
Only these allowlisted fields enter models. Exclude labels, injury/damage/towing
outcomes, event reconstruction, sampling strata, IDs, weights, `*NAME` labels,
and NHTSA-imputed fields. Unlisted fields need separate review.

Aggregate vehicles once each and identify drivers using `PER_TYP=1`, not
`PER_NO=1`. Keep unmatched drivers in crash summaries and never select records
by severity. Age ranges summarize known values only. Vehicle ages cover the
vehicle table; `VE_TOTAL` also includes parked/working vehicles. The model-year
range 1886 through crash year plus one is our validation rule. Behavior flags
are positive if any recorded value is positive, negative only for nonempty
all-negative groups, and otherwise missing. Missing drivers never drop a crash.

## Predictor availability

This is conditional severity prediction among reported crashes using completed
records, as described in the [proposal](../reports/proposal/crss_crash_severity_proposal.pdf).
Core fields do not have verified live availability. Reported speeding and drinking
are retrospective-only additions: investigation and reporting may depend on
severity. Better expanded scores do not establish pre-crash prediction or
causation. Earlier prediction would require a defined prediction time and
verified input availability. Both target definitions use the same exclusions.

## Reusable feature preprocessing

`prepare_features.py` constructs training and validation features, checks their
source hashes against the data manifest, and excludes unknown targets. It does
not read 2024 data or train a model. Rebuild data if hashes differ.

| Input | Treatment |
|---|---|
| Categorical | Fill missing with -1 and one-hot encode training categories. |
| Numeric | Fill with training median and standardize; all-empty training columns stay present with zero fallback. |
| Unseen category | All-zero block for that field, with unchanged column order. |

`make_preprocessor("core")` or `make_preprocessor("expanded")` returns a
scikit-learn pipeline. Keep `YEAR_FILE` in the input: fitting rejects years
outside 2020-2022, then drops metadata. Use `transform` on later years.
`scale_numeric=False` skips scaling for tree models. Fit separately inside each
training fold if cross-validation is used. Never fit on holdouts.

Each folder in `data/processed/features/{core,expanded}/` contains:

| Files | Contents |
|---|---|
| `train.npz`, `validation.npz` | Sparse matrices; load with `scipy.sparse.load_npz`. |
| `train_rows.csv`, `validation_rows.csv` | Matching crash keys and labels in matrix row order. |
| `columns.csv` | Encoded column names in order. |
| `preprocessor.joblib` | Fitted pipeline; load with `joblib.load`. |
| `metadata.json` | Exclusion counts, configuration, versions, and hashes. |

Rerunning replaces these local artifacts. Core and expanded use the same eligible
rows; their encoded widths may differ. Missing predictors do not remove rows.

## Majority-class baseline

After preparing features, run `python run_majority_baseline.py` from `notebooks/`,
or use [Majority Baseline.ipynb](../notebooks/Majority%20Baseline.ipynb).
`DummyClassifier(strategy="most_frequent")` learns the unweighted majority label
from 2020?2022 and evaluates both feature sets on the same eligible 2023 crashes.
It does not read the 2024 test set. Ties follow scikit-learn's sorted class order.

[Results](../results/majority_baseline/metrics.csv) include accuracy, macro-F1,
per-class scores, and confusion counts. Macro-F1 averages low, moderate, and high;
undefined scores are zero. `run.json` records input/code hashes and exclusions.
Crash-level predictions stay in `data/processed/predictions/majority_baseline/`.
Rerunning replaces these outputs.

Both sets predict moderate: validation accuracy is 64.89%, macro-F1 is 0.2624,
and high-severity recall is 0. This is the minimum benchmark for later models.

## Logistic Regression

Run `python run_logistic_regression.py` from `notebooks/` after preparing features,
or use [Logistic Regression.ipynb](../notebooks/Logistic%20Regression.ipynb).
Both configurations reuse training-fitted preprocessing and train on 2020?2022.
Fixed settings: multinomial loss, `lbfgs`, L2 (`l1_ratio=0`), `C=1`, no class
weighting, `max_iter=1000`, `tol=1e-4`, and seed 42. Nonconvergence stops the run.
Regularization and class-weight tuning are reserved for BASE-05.

[Validation metrics](../results/logistic_regression/metrics.csv), per-class scores,
confusion counts, and run settings are saved in `results/logistic_regression/`.
Predictions, class probabilities, and fitted pipelines stay local in
`data/processed/predictions/logistic_regression/`. Pipelines accept the crash-level
feature table from `build_feature_table`, including `YEAR_FILE`, and apply the
saved preprocessing before prediction. The run does not read 2024 data.

## Reports and checks

Reports describe local raw files unless marked as processed or training-only.

| Reports | Contents |
|---|---|
| [Raw schema](../docs/crss_schema.md), [inventory](../docs/crss_inventory.csv) | All 28 tables across five years; columns, file sizes, hashes, and source URLs. |
| [Join audit](../docs/crss_join_audit.csv) | Key coverage and crash counts. |
| [Missingness](../docs/crss_missingness.csv), [special codes](../docs/crss_special_codes.csv), [coding changes](../docs/crss_coding_changes.csv), [code checks](../docs/crss_code_checks.csv) | Blanks, coded missingness, structural changes, and validation flags. |
| [Training severity](../docs/crss_severity_training.csv), [target counts](../docs/crss_target_counts.csv), [target comparison](../docs/crss_target_comparison.csv) | Training-only label review. |
| [Processed schema](../docs/crss_processed_schema.csv), [processed checks](../docs/crss_processed_checks.csv) | Output columns and split integrity. |

Run these from the repository root as needed:

```bash
python src/data/document_raw.py
python -m src.data.audit_codes
python -m src.data.severity
python -m unittest discover -s tests -v
```

Supplementary tables need review before joining. Use holdout audits only for
compatibility checks, not feature selection or fitted preprocessing decisions.

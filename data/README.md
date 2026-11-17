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
It leaves the data unchanged. The notebook checks duplicate keys and join
coverage separately; see [crash-level joins](#crash-level-joins) and the
[join report](../docs/crss_join_audit.csv).

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

The [severity rules](#crash-severity-rules) explain label precedence and
missing outcomes. The [training report](../docs/crss_severity_training.csv)
lists 2020–2022 class counts and reasons. Run `python -m src.data.severity`
from the repository root to regenerate that report and the
[target counts](../docs/crss_target_counts.csv) and
[target comparison](../docs/crss_target_comparison.csv), without reading holdout years.
The comparison checks the combined labels against injury-only labels on the
same training crashes.

## Crash-level joins

We keep one row per crash using `YEAR_FILE` and `CASENUM`. The notebook groups
person and vehicle records by these keys before attaching severity to the
accident table. This avoids multiplying rows when a crash has several vehicles
or people.

The shared checks are in `src/data/joins.py`. Run the preprocessing notebook
from `notebooks/` to use them and update [the join report](../docs/crss_join_audit.csv).
The report uses our local raw files and includes the final crash count by year.

### Checks before joining

- Accident keys: `YEAR_FILE`, `CASENUM`.
- Vehicle keys: `YEAR_FILE`, `CASENUM`, `VEH_NO`.
- Person keys: `YEAR_FILE`, `CASENUM`, `VEH_NO`, `PER_NO`.

Missing or duplicate keys stop the notebook. Vehicle and person records must
also have a matching accident. These checks run before grouping, so aggregation
cannot hide duplicate input records.

We check person-to-vehicle coverage using the vehicle key. People with
`VEH_NO = 0` are counted separately because they have no vehicle link. Other
unmatched vehicle keys are reported, not dropped. Every person still contributes
to the summary for their crash. The report does not establish why a vehicle
link is missing; check the source records and manuals before using those links
for vehicle or driver features.

### Checks during joining

The summary joins use pandas' `one_to_one` validation. The final join starts
from the accident table and keeps every original crash key. Duplicate summary
keys, unexpected crash keys, overlapping columns, or changed crash counts stop
the join. The notebook also compares the before/after counts for each year.

The classifier starts with every accident key and attaches person and vehicle
summaries. Crashes without people stay in the table with an `unknown` label.
See [severity rules](#crash-severity-rules) for the labeling decisions.

### Current data

All five years pass the raw-key checks. Every crash has vehicle records.
The report lists crashes without people and people without matching vehicles
by year. These gaps are kept visible rather than removed by an inner join.

The final table has 264,661 crashes: 162,900 from 2020–2022, 50,103 from 2023,
and 51,658 from 2024. There are 81 crashes without person records.

Run the focused tests from the repository root:

```bash
python -m unittest discover -s tests -p test_data_joins.py -v
```

On macOS, use `python3`. The tests cover repeated crash numbers across years,
missing matches, duplicate or missing keys, and records without a parent crash.

## Crash severity rules

We assign one label per crash using all person and vehicle records. The rules
are in `src/data/severity.py`. They are fixed rules, with no fitted thresholds.

### Label order

| Label | Rule |
|---|---|
| High | Any person has `INJ_SEV` 3 or 4 (serious or fatal injury). |
| Moderate | No known high injury, and any person has injury code 1 or 2, any vehicle has `TOWED` 2, 3, 6, or 7, or any vehicle has `DEFORMED` 6. Requires at least one person record. |
| Low | At least one person and vehicle record, every person has injury code 0, every vehicle has `TOWED` 5, and every vehicle has damage code 0, 2, or 4. |
| Unknown | No person records, or the available outcomes do not meet any rule above. |

High takes precedence over moderate, and moderate over low. We keep the existing
decision that towing for any reason counts as moderate, including code 3.
Functional damage (code 4) alone can still be low.

### Why combine injury and vehicle outcomes?

The proposed target measures crash consequences: harm to people or disruption
to the vehicle. Moderate groups non-serious injuries with towing or disabling
damage because either can make a crash consequential without a known serious
or fatal injury. This is our project definition, not a clinical injury scale.

Those consequences are not equivalent. A vehicle can be towed without disabling
damage, and towing alone does not establish bodily harm. In particular, `TOWED`
3 explicitly means towing without disabling damage. We keep that choice in the
proposed target so we can test it against a simpler injury-only definition,
rather than assume the combined category is the better target.

### Injury-only alternative

The classifier also returns `INJURY_ONLY_SEVERITY` using all people in each crash:

| Label | Rule |
|---|---|
| High | Any injury code 3 or 4. |
| Moderate | No known high injury, and any injury code 1 or 2. |
| Low | At least one person, and every injury code is 0. |
| Unknown | No people, or insufficient known injury information. |

The same evidence precedence applies: a known high or moderate injury takes
priority over another person's unresolved injury. Vehicle outcomes have no effect
on this label. Both labels are outcomes and must be excluded from predictors.

#### Training comparison

These counts use the same 162,900 crashes from 2020–2022. Unknowns remain in the
comparison so we can see which definition can label each crash.

| Label | Combined | Injury-only |
|---|---:|---:|
| Low | 28,742 | 69,961 |
| Moderate | 92,261 | 62,745 |
| High | 21,699 | 21,699 |
| Unknown | 20,198 | 8,495 |

Rows below are combined labels; columns are injury-only labels.

| Combined / injury-only | Low | Moderate | High | Unknown |
|---|---:|---:|---:|---:|
| Low | 28,742 | 0 | 0 | 0 |
| Moderate | 27,187 | 62,745 | 0 | 2,329 |
| High | 0 | 0 | 21,699 | 0 |
| Unknown | 14,032 | 0 | 0 | 6,166 |

43,548 crashes (26.7%) change labels. Of those, 27,187 move from combined
moderate to injury-only low because towing or damage supplies the moderate
evidence. Another 2,329 move from moderate to unknown because injury evidence
alone is insufficient. The remaining 14,032 move from unknown to low because
injuries are all known to be zero but vehicle outcomes do not establish low.
High labels match exactly. This shows sensitivity to the definition, not which
definition is more accurate.

The [class-count report](../docs/crss_target_counts.csv) and
[cross-tabulation](../docs/crss_target_comparison.csv) include each training year and
the pooled training total (`all_training`). Do not add the pooled rows to the
individual-year rows. `changed` marks off-diagonal label pairs; sum their `rows`
within a scope to count changed labels.

#### Later model comparison

Keep the combined target as the proposed primary analysis and injury-only as
the sensitivity analysis. Use the same chronological splits, predictor set,
model families, and tuning budget for both. Fit preprocessing on training only.
For the direct comparison, use crashes with known labels under both definitions:
140,373 training crashes. Report results on each definition's full eligible
population separately, including exclusion counts, because those populations
differ. Do not use either target or its component outcomes as predictors.

Report macro-F1, per-class metrics, high-severity recall, and confusion matrices
for each definition. Scores describe different targets; a higher score does not
establish a better severity definition. Use 2023 for model selection and reserve
2024 for the fixed final analyses. No models have been compared in this step.

### Missing and ambiguous outcomes

Injury codes 5, 6, and 9 do not establish a low, moderate, or high injury level.
Code 6 means death before the crash, so it is not a crash fatality. Tow codes
8 and 9 and damage codes 7, 8, and 9 do not establish low outcomes either.
Blank values and unexpected codes are also unresolved.

A known serious or fatal injury still makes a crash high when another outcome
is unknown. A known moderate outcome still makes it moderate when other
outcomes are unknown. That is a project convention based on observed evidence;
it does not prove an unknown injury was less serious. Low requires every outcome
to be known and meet the low rule.

We keep crashes without people as unknown, even if towing or damage is recorded.
This preserves the notebook's existing conservative choice for those records.
Without vehicle records, a known injury can establish high or moderate, but a
crash cannot be low. Missing vehicle matches never count as evidence of towing.

Each label has one `SEVERITY_REASON`. If several rules apply, the reason order
is serious/fatal injury, minor/possible injury, towing, then disabling damage.
Unknown reasons distinguish no people, no vehicles, and unresolved outcomes.
If both tables are missing, the reason is `no_person_records`.
These reasons explain the decision; they are not model features.

### Training review

This review uses the 2020–2022 raw files. Code/name pairs in those files were
checked against the existing mapping. See the [NHTSA manuals](README.md#source)
for field definitions. The code lists and precedence above are fixed before
applying this implementation to validation or test years. Do not change the
rules based on holdout distributions or model performance.

The earlier notebook inspected codes and outcomes across all five years.
That exposure cannot be undone, so we cannot claim the original rule design
was completely independent of the holdout data. This update removes those
pooled outcome inspections and restricts the rule-review report to training.

| Training label | Crashes |
|---|---:|
| Low | 28,742 |
| Moderate | 92,261 |
| High | 21,699 |
| Unknown | 20,198 |
| Total | 162,900 |

The [training report](../docs/crss_severity_training.csv) breaks these counts down by
year and reason. Fractions use every crash in that year, including unknowns.
Exclude the 20,198 unknown training rows when fitting the three-class model;
142,702 training crashes remain. Keep unknowns in the processed files so we can
report exclusions for each split. Report holdout label counts during evaluation,
after the rules are fixed.

From the repository root, regenerate all three training reports with:

```bash
python -m src.data.severity
```

This command reads only 2020–2022 and leaves the raw and processed CSVs unchanged.
The reporting functions reject validation or test rows. The notebook applies
the same classifier to every year and currently saves only the primary
`SEVERITY` with the crash table. The alternative label is available in the
classifier output for the later model comparison; reasons are kept out of the
processed feature table.

Run the tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

On macOS, use `python3`. Tests cover precedence, multiple people and vehicles,
all listed unknown codes, blanks, unexpected codes, and missing records.

## Predictor availability

Our goal is crash-severity prediction, with classification models predicting
the severity category. The current analysis uses completed CRSS records and
does not yet establish prediction before the outcome is known. A variable can avoid directly giving
away the label and still be unavailable when a real-time prediction is needed.

Before building features, review every candidate field and record:

| Field to document | What we need |
|---|---|
| Variable and source | Exact column, table, years, and manual reference. |
| Meaning | What the variable measures and how it is recorded. |
| Availability | When an operator could actually obtain it: before the crash, at initial reporting, after investigation, or unresolved. |
| Outcome relationship | Whether it defines the target, reveals the outcome, or may be inferred from the outcome during investigation. |
| Decision | Include in retrospective analysis, exclude, or leave pending, with a reason. |

This is the review requirement, not a completed field-by-field audit. The final
predictor list has not been approved. Pending fields stay out until reviewed.

### Rules for the feature review

Exclude injury, damage, towing, airbag deployment, both severity labels, label
reasons, and other outcome-derived fields from both target comparisons. Changing
to injury-only labels does not make vehicle outcomes acceptable predictors for
this comparison. Keep IDs and survey-design fields out of predictors; use
`WEIGHT` only if the analysis calls for sample weighting.

Driver behavior, impairment, and other findings from an investigation need an
explicit availability review. Do not assume that describing a pre-crash action
means the information was recorded or available before the outcome. Review
roadway, environmental, and vehicle fields too; membership in the core feature
group does not establish availability.

For a retrospective model, an investigation-derived field may be considered
only after checking how it was recorded and whether the outcome influenced its
coding. Document that limitation. For any future model claiming earlier
prediction, first define the exact prediction time and inputs available then.
Only admit fields with evidence that they are available by that time. An
unresolved availability claim is not enough.

Use the [NHTSA manuals](README.md#source) for the review. Fit data-driven
feature choices on training data only. Keep the reviewed predictor set the
same for the combined and injury-only target comparison.

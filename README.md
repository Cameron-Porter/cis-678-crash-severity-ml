# CIS 678 - Crash Severity Prediction Using Machine Learning

Predicting severity among police-reported crashes using NHTSA CRSS data from
2020-2024. We compare a majority-class baseline, Logistic Regression, Random
Forest, and XGBoost. See the [proposal](reports/proposal/crss_crash_severity_proposal.pdf).

The primary target combines injury and vehicle consequences into low, moderate,
and high severity. We also compare an injury-only definition. Unresolved outcomes
remain `unknown` and are excluded from modeling. The [data guide](data/README.md)
contains the rules, feature definitions, and reproducible commands.

## Team

| Member | Lead responsibility |
|---|---|
| Vinnie Gambotto | Data preparation, joins, severity labels |
| Cameron Porter | Baselines and feature engineering |
| Zachary Stevens | Random Forest and XGBoost |
| Payton Wilder | Evaluation and feature analysis |

## Setup

Use Python 3.13 as recommended in `requirements.txt`.

```bash
git clone https://github.com/Cameron-Porter/cis-678-crash-severity-ml.git
cd cis-678-crash-severity-ml
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` on Windows or
`source .venv/bin/activate` on macOS/Linux, then install dependencies:

```bash
python -m pip install -r requirements.txt
```

[Download the data](data/README.md#downloading-the-data), then run:

```bash
cd notebooks
python build_data.py
python prepare_features.py
python run_majority_baseline.py
python run_logistic_regression.py
python tune_baselines.py
python export_baselines.py
```

Use `python3` on macOS. Run these commands from `notebooks/`; the notebooks
there expose the same steps. Datasets and fitted artifacts stay local.
The final command creates `data/processed/baseline_handoff.zip` for evaluation.
See the [handoff format](data/README.md#baseline-handoff) and
[validation results](results/baseline_handoff/metrics.csv).

## Modeling rules

| Split | Years | Use |
|---|---|---|
| Training | 2020-2022 | Fit models and preprocessing |
| Validation | 2023 | Tune and select models |
| Test | 2024 | Final evaluation only |

Compare the [core and expanded feature sets](data/README.md#core-and-expanded-feature-sets)
using the same eligible crashes. Fit imputation, encoding, and scaling on
training only. Keep target components, IDs, and survey metadata out of predictors.

Primary metric: **macro-F1**. Also report accuracy, per-class precision/recall/F1,
high-severity recall, and confusion matrices. Compare class weighting during tuning.

These models use completed crash records. Driver behavior fields can be recorded
during investigation, so results do not establish pre-crash prediction. See
[predictor availability](data/README.md#predictor-availability).

## Repository

| Folder | Purpose |
|---|---|
| `data/` | Local raw and processed datasets |
| `notebooks/` | Step-by-step workflows and exploration |
| `src/` | Shared data, feature, model, and evaluation code |
| `tests/` | Automated checks |
| `docs/` | Schemas, feature catalog, and audit reports |
| `results/` | Metrics and plots |
| `reports/` | Proposal and final deliverables |

## Contributing

Work on a feature branch and open a PR to `main`. Keep changes focused on an
issue, describe the change and validation, and use `Closes #<issue>` when complete
or `Refs #<issue>` for partial work. Require a teammate's review before merging;
do not push directly to `main`. Update dependencies when adding packages.

Run checks from the repository root:

```bash
python -m unittest discover -s tests -v
```

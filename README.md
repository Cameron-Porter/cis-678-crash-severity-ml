# CIS 678 – Crash Severity Prediction Using Machine Learning

Machine learning project predicting motor vehicle crash severity using NHTSA Crash Report Sampling System (CRSS) data from 2020–2024, comparing Logistic Regression, Random Forest, and XGBoost.

## Project Overview

This project is being developed as part of CIS 678 at Grand Valley State University.

Our goal is to investigate how accurately machine learning models can classify the severity of motor vehicle crashes using roadway, environmental, vehicle, and driver-related characteristics.

We predict severity as a category, making this a classification task. The current
analysis uses completed crash records. It does not yet establish prediction
before the outcome is known; each predictor's availability needs to be reviewed.

We will classify crashes into three severity categories:

- **Low:** No recorded injuries or significant damage, where sufficient outcome information is available.
- **Moderate:** Less serious or possible injuries, or qualifying vehicle damage/tow-away outcomes.
- **High:** Serious or fatal injuries.

The [classification rules](data/README.md#crash-severity-rules) define label precedence and
missing-outcome handling. Crashes that cannot be labeled stay `unknown` in the
processed files and are excluded from the three-class model.

We also compare these combined labels with an injury-only definition. The
[training comparison](data/README.md#training-comparison) shows how the
choice changes class counts; model comparisons will follow.

We will implement and compare:

1. **Majority-Class Baseline** – Predicts the most frequent severity category.
2. **Logistic Regression** – Provides an interpretable baseline model.
3. **Random Forest** – Uses an ensemble of decision trees to capture nonlinear relationships.
4. **XGBoost** – Uses gradient-boosted trees to improve predictive performance.

All models will use consistent data splits and evaluation metrics to support fair comparisons.

## Team Members

| Team Member | Primary Responsibility |
|---|---|
| Vinnie Gambotto | Data preparation, joins, and severity classification |
| Cameron Porter | Baseline models and feature engineering |
| Zachary Stevens | Random Forest and XGBoost |
| Payton Wilder | Evaluation, metrics, and feature analysis |

These are primary responsibilities. All team members will contribute to reviewing results, documentation, and the final report.

## Project Structure

To keep the project organized and make collaboration easier, please follow the directory structure below when adding files.

```text
cis-678-crash-severity-ml/
├── README.md
├── requirements.txt              # Shared Python dependencies
├── .gitignore
│
├── data/
│   ├── raw/                      # Original NHTSA CRSS datasets
│   └── processed/                # Cleaned, merged, and labeled datasets
│
├── notebooks/
│   └── exploration.ipynb         # Exploratory data analysis
│
├── src/
│   ├── data/
│   │   ├── load.py               # Dataset loading
│   │   └── preprocess.py         # Data cleaning and preparation
│   │
│   ├── features/
│   │   └── build_features.py     # Feature selection and engineering
│   │
│   ├── models/
│   │   ├── majority_baseline.py  # Majority-class baseline
│   │   ├── logistic_regression.py
│   │   ├── random_forest.py
│   │   └── xgboost_model.py
│   │
│   └── evaluation/
│       └── evaluate.py           # Shared evaluation metrics
│
├── tests/                        # Automated tests
├── results/                      # Metrics, plots, and experiment outputs
├── reports/
│   ├── proposal/                 # Project proposal
│   └── final/                    # Final report and presentation
│
└── docs/                         # Additional documentation
```

This is the intended project structure. Some files and directories may not exist until their respective tasks are started.

### Directory Guidelines

- **`data/`** – Stores raw and processed CRSS datasets locally. Large datasets should not be committed to GitHub. Document download sources and processing steps.
- **`notebooks/`** – Used for exploratory analysis and experimentation. Move reusable code into `src/` when appropriate.
- **`src/data/`** – Handles loading, joining, cleaning, and preparing CRSS data.
- **`src/features/`** – Contains feature selection and engineering logic shared across models.
- **`src/models/`** – Contains individual model implementations.
- **`src/evaluation/`** – Contains shared evaluation functions and metrics.
- **`tests/`** – Contains tests for preprocessing, feature engineering, and model functionality.
- **`results/`** – Stores metrics, confusion matrices, plots, and experiment outputs. Commit only relevant, reasonably sized results.
- **`reports/`** – Contains the project proposal, final report, and presentation.
- **`docs/`** – Contains additional technical documentation and methodology notes.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Cameron-Porter/cis-678-crash-severity-ml.git
cd cis-678-crash-severity-ml
```

### 2. Create a Python Virtual Environment

```bash
python -m venv .venv
```

Activate the environment.

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

When adding a new dependency, update `requirements.txt` so other team members can reproduce the environment.

### 4. Obtain the Dataset

The project uses NHTSA CRSS data from 2020–2024.

Dataset information is available from the [NHTSA CRSS website](https://www.nhtsa.gov/crash-data-systems/crash-report-sampling-system).

Raw datasets should be stored locally under `data/raw/`.

Processed datasets should be stored under `data/processed/`.

Follow the [data guide](data/README.md) to download the files. Then run
`python build_data.py` from `notebooks/` (`python3` on macOS) to rebuild and check
the three processed datasets. The preprocessing notebook uses the same code.
See the [processed schema](docs/crss_processed_schema.csv) for column roles;
retained fields still need review before use as predictors.

## Data Preparation and Model Evaluation

To ensure consistent results, all models must use the same crash-level severity definitions and chronological data splits.

### Dataset Splits

| Dataset | Years | Purpose |
|---|---|---|
| Training | 2020–2022 | Model training and preprocessing |
| Validation | 2023 | Hyperparameter tuning and model selection |
| Testing | 2024 | Final model evaluation |

The 2024 test dataset must not be used for feature selection, preprocessing decisions, hyperparameter tuning, or model selection.

### Feature Engineering

We will compare two feature groups:

- **Core features:** Roadway, environmental, and vehicle-related characteristics.
- **Expanded features:** Core features plus driver-related characteristics.

Each candidate must pass the [predictor availability review](data/README.md#predictor-availability).
Record when it becomes available and whether it reveals the outcome. Driver
findings recorded during an investigation cannot be assumed available for
earlier prediction. The final feature list is still pending review.

Categorical variables must be encoded appropriately, and missing values handled consistently.

Preprocessing transformations that learn from the data must be fitted using training data only to avoid data leakage.

Injury outcomes, damage outcomes, towing information, airbag deployment, and derived severity fields must not be included as predictors because they could reveal the target severity classification.

### Evaluation Metrics

Our primary evaluation metric is **macro-averaged F1 score**, which gives equal importance to each severity category.

Additional metrics include:

- Accuracy
- Per-class precision
- Per-class recall
- Per-class F1 score
- Confusion matrices
- High-severity recall

We will also examine class imbalance and compare the effect of class weighting where appropriate.

All models must use the same test data and target definitions to ensure meaningful comparisons.

## Branching and Pull Request Workflow

To keep `main` stable and avoid conflicts, all team members should work on separate feature branches and submit pull requests (PRs) before merging changes.

### 1. Create a Feature Branch

Before starting work, make sure your local `main` branch is up to date:

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

Use descriptive branch names, such as:

- `feature/data-preprocessing`
- `feature/logistic-regression`
- `feature/random-forest`
- `feature/model-evaluation`

Each branch should focus on one feature, task, or related set of changes.

### 2. Commit and Push Changes

Make changes on your feature branch, then commit and push them to GitHub:

```bash
git add .
git commit -m "feat: describe your changes"
git push -u origin feature/your-feature-name
```

Commit regularly with meaningful messages.

Examples:

- `feat: implement logistic regression baseline`
- `fix: correct severity label mapping`
- `docs: update dataset processing instructions`
- `test: add preprocessing validation tests`

### 3. When to Create a Pull Request

Create a pull request when:

- A feature or assigned task is complete and ready for review.
- Your code runs successfully and has been tested.
- You want feedback on work in progress (use a **Draft PR**).
- You're ready to integrate your changes into `main`.

Avoid creating one massive pull request at the end of the project. Smaller, focused PRs are easier to review and merge.

### 4. How to Create a Pull Request

1. Open the repository on GitHub.
2. Navigate to **Pull requests → New pull request**.
3. Set the **base branch** to `main`.
4. Set the **compare branch** to your feature branch.
5. Provide a descriptive title and summary of your changes.
6. **Reference the related GitHub Issue** in the PR description using `Closes #<issue-number>`.
7. Assign at least one other team member as a reviewer.
8. Select **Create pull request**.

#### Pull Request Description Template

Use the following format when creating a PR:

```markdown
## Summary
Briefly describe what was implemented or changed.

## Related Issue
Closes #123

## Changes Made
- Describe the primary changes.
- List any new files or functionality.
- Note any changes to existing behavior.

## Testing
- [ ] Code runs successfully.
- [ ] Relevant tests pass.
- [ ] No existing functionality is broken.

## Additional Notes
Include any relevant considerations, limitations, or follow-up work.
```

Replace `#123` with the actual GitHub Issue number.

**Important:** Using `Closes #123`, `Fixes #123`, or `Resolves #123` in a PR description automatically closes the referenced issue when the PR is merged into `main`.

For work that only partially addresses an issue, use `Refs #123` instead. This links the PR to the issue without automatically closing it.

#### Pull Request Guidelines

- Every PR should reference at least one related GitHub Issue.
- Keep PRs focused on a single issue or closely related changes.
- Use Draft PRs for incomplete work that needs early feedback.
- Ensure the issue's acceptance criteria are satisfied before requesting approval.
- Do not manually close an issue until its required work is complete.
- If a PR completes multiple issues, reference each one separately using its actual issue number.

### 5. Review and Merge

Before merging:

- At least one other team member should review and approve the PR.
- Address any requested changes or comments.
- Confirm the changes don't break existing functionality.
- Resolve merge conflicts if necessary.
- Ensure the PR is up to date with `main` when required.

Once approved, select **Squash and merge** to merge into `main`.

**Do not push directly to `main`.** All changes should go through the pull request process.

### 6. Sync Your Local Repository

After a PR is merged, update your local `main` before starting your next task:

```bash
git checkout main
git pull origin main
git checkout -b feature/next-task
```

This ensures new work starts from the latest shared code.

## Development Guidelines

To keep our code consistent and avoid unnecessary conflicts, please follow these guidelines:

1. **Follow the project structure.** Place new files in the appropriate directories rather than creating unnecessary top-level folders.
2. **Keep code reusable.** Shared functionality should be implemented in `src/` rather than duplicated across notebooks or model implementations.
3. **Document dependencies.** Add required Python packages to `requirements.txt`.
4. **Avoid committing large files.** Raw datasets, processed datasets, trained models, virtual environments, and temporary files should remain outside version control unless explicitly agreed upon.
5. **Maintain reproducibility.** Use consistent data splits, document training configurations, and set random seeds where applicable.
6. **Prevent data leakage.** Never use test data or outcome-derived severity information as model inputs.
7. **Coordinate shared changes.** Discuss significant modifications to preprocessing, feature engineering, or evaluation logic with affected team members.
8. **Test before merging.** Verify that new functionality works and does not break existing code.
9. **Document important decisions.** Update the README or relevant documentation when workflows, data definitions, or modeling approaches change.

## Project Deliverables

The final project will include:

- A reproducible CRSS data preparation pipeline.
- Documented crash severity classification rules.
- Majority-class and Logistic Regression baselines.
- Random Forest and XGBoost implementations.
- Consistent model evaluation and comparison.
- Analysis of feature importance and model limitations.
- Final project report and presentation.

## References

- [NHTSA Crash Report Sampling System (CRSS)](https://www.nhtsa.gov/crash-data-systems/crash-report-sampling-system)
- [scikit-learn Documentation](https://scikit-learn.org/stable/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/en/stable/)

---

**Grand Valley State University – CIS 678**

*This repository is maintained collaboratively by the project team for academic purposes.*

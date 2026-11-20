# XGBoost Model

# XGBoost
import json
import platform
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn
import xgboost

from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src.data.joins import CRASH_KEY, check_keys
from src.data.preprocess import sha256
from src.evaluation.evaluate import LABELS, evaluate_predictions
from sklearn.metrics import f1_score, accuracy_score, recall_score

# XGBoost uses numeric class labels internally.
# Preserve the project's severity labels for evaluation and reporting.
CLASS_LABELS = list(LABELS)
LABEL_TO_INT = {label: i for i, label in enumerate(CLASS_LABELS)}
INT_TO_LABEL = {i: label for label, i in LABEL_TO_INT.items()}


PARAMETERS = dict(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=1.0,
    colsample_bytree=1.0,
    objective="multi:softprob",
    eval_metric="mlogloss",
    tree_method="hist",
    random_state=42,
    n_jobs=-1
)


def fit_xgboost_models(inputs, *, parameters=None):
    models = {}

    settings = PARAMETERS | (parameters or {})

    for configuration, item in inputs.items():
        matrix, rows = item["train"]

        check_keys(rows, CRASH_KEY, "training")

        if rows.empty or not rows.YEAR_FILE.isin([2020, 2021, 2022]).all():
            raise ValueError(
                "Fit XGBoost on 2020-2022 training rows only"
            )

        if set(rows.SEVERITY) != set(LABELS) or matrix.shape[0] != len(rows):
            raise ValueError(
                "Training requires all three severity classes and aligned rows"
            )

        y_train = rows.SEVERITY.map(LABEL_TO_INT)

        model = XGBClassifier(**settings)

        model.fit(matrix, y_train)

        models[configuration] = model

    return models


def evaluate_xgboost_models(inputs, models):
    results = {}

    for configuration, model in models.items():
        matrix, rows = inputs[configuration]["validation"]

        check_keys(rows, CRASH_KEY, "validation")

        if rows.empty or not rows.YEAR_FILE.eq(2023).all():
            raise ValueError(
                "Evaluate XGBoost on 2023 validation only"
            )

        if matrix.shape[0] != len(rows):
            raise ValueError(
                "Validation matrix and rows must be aligned"
            )

        predicted_numeric = model.predict(matrix)

        predicted = np.array([
            INT_TO_LABEL[int(value)]
            for value in predicted_numeric
        ])

        metrics, per_class, confusion = evaluate_predictions(
            rows.SEVERITY, predicted
        )

        output = rows[CRASH_KEY].copy()
        output["y_true"] = rows.SEVERITY.to_numpy()
        output["y_pred"] = predicted

        probabilities = model.predict_proba(matrix)

        for label in LABELS:
            class_number = LABEL_TO_INT[label]
            class_index = list(model.classes_).index(class_number)

            output[f"p_{label}"] = probabilities[:, class_index]

        metrics.update(
            configuration=configuration,
            train_rows=len(inputs[configuration]["train"][1]),
            validation_rows=len(rows),
            n_estimators=model.n_estimators
        )

        results[configuration] = dict(
            metrics=metrics,
            per_class=per_class,
            confusion=confusion,
            predictions=output
        )

    return results


def save_xgboost_results(root, inputs, models, results):
    root = Path(root)

    report = root / "results" / "xgboost"
    local = root / "data/processed/predictions/xgboost"

    pipelines = {}

    for configuration, model in models.items():
        folder = root / "data/processed/features" / configuration
        metadata = inputs[configuration]["metadata"]
        path = folder / "preprocessor.joblib"

        if sha256(path) != metadata["files"][path.name]:
            raise ValueError(
                "Preprocessor hash mismatch; rerun prepare_features.py"
            )

        if metadata["sklearn"] != sklearn.__version__:
            raise ValueError(
                "Rebuild features with the current scikit-learn version"
            )

        preprocessor = joblib.load(path)

        pipelines[configuration] = Pipeline([
            ("preprocess", preprocessor),
            ("model", model)
        ])

    report.mkdir(parents=True, exist_ok=True)
    local.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        [r["metrics"] for r in results.values()]
    ).to_csv(
        report / "metrics.csv",
        index=False,
        lineterminator="\n"
    )

    for name in ("per_class", "confusion"):
        pd.concat(
            [
                r[name].assign(configuration=c)
                for c, r in results.items()
            ],
            ignore_index=True
        ).to_csv(
            report / f"{name}.csv",
            index=False,
            lineterminator="\n"
        )

    hashes = {}

    for configuration, result in results.items():
        path = local / f"{configuration}_validation.csv"

        result["predictions"].to_csv(
            path,
            index=False,
            lineterminator="\n"
        )

        hashes[path.relative_to(root).as_posix()] = sha256(path)

        joblib.dump(
            pipelines[configuration],
            local / f"{configuration}_pipeline.joblib"
        )

    run = dict(
        model="XGBClassifier",
        parameters={
            c: m.get_params()
            for c, m in models.items()
        },
        versions=dict(
            python=platform.python_version(),
            sklearn=sklearn.__version__,
            xgboost=xgboost.__version__,
            numpy=np.__version__,
            pandas=pd.__version__,
            scipy=scipy.__version__
        ),
        labels=list(LABELS),
        label_encoding=LABEL_TO_INT,
        zero_division=0,
        fit_years=[2020, 2021, 2022],
        evaluation_year=2023,
        sample_weight=None,
        feature_metadata_sha256={
            c: i["metadata_sha256"]
            for c, i in inputs.items()
        },
        exclusions={
            c: i["metadata"]["exclusions"]
            for c, i in inputs.items()
        },
        prediction_hashes=hashes,
        source_hashes={
            p.relative_to(root).as_posix(): sha256(p)
            for p in (
                root / "src/models/xgboost.py",
                root / "src/models/data.py",
                root / "src/evaluation/evaluate.py"
            )
        }
    )

    (report / "run.json").write_text(
        json.dumps(run, indent=2, sort_keys=True) + "\n",
        encoding="utf8"
    )


def tune_xgboost(inputs):

    configurations = [
        {"n_estimators": 100, "max_depth": 3, "learning_rate": 0.1, "subsample": 1.0},
        {"n_estimators": 100, "max_depth": 6, "learning_rate": 0.1, "subsample": 1.0},
        {"n_estimators": 100, "max_depth": 9, "learning_rate": 0.1, "subsample": 1.0},
        {"n_estimators": 200, "max_depth": 3, "learning_rate": 0.1, "subsample": 1.0},
        {"n_estimators": 200, "max_depth": 6, "learning_rate": 0.1, "subsample": 1.0},
        {"n_estimators": 200, "max_depth": 3, "learning_rate": 0.05, "subsample": 1.0},
        {"n_estimators": 200, "max_depth": 6, "learning_rate": 0.05, "subsample": 1.0},
        {"n_estimators": 300, "max_depth": 3, "learning_rate": 0.05, "subsample": 0.8},
        {"n_estimators": 300, "max_depth": 6, "learning_rate": 0.05, "subsample": 0.8},
        {"n_estimators": 200, "max_depth": 3, "learning_rate": 0.2, "subsample": 0.8}
    ]

    tuning_results = []
    best_models = {}

    for feature_set in ["core", "expanded"]:

        X_train, train_rows = inputs[feature_set]["train"]
        X_val, val_rows = inputs[feature_set]["validation"]

        if (
            train_rows.empty
            or not train_rows.YEAR_FILE.isin([2020, 2021, 2022]).all()
            or val_rows.empty
            or not val_rows.YEAR_FILE.eq(2023).all()
        ):
            raise ValueError("Tuning requires 2020-2022 training and 2023 validation data")

        y_train = train_rows["SEVERITY"].map(LABEL_TO_INT)
        y_val = val_rows["SEVERITY"]

        best_score = -1

        for i, params in enumerate(configurations):

            print(
                f"Training {feature_set}, configuration {i + 1}/{len(configurations)}...",
                flush=True
            )

            model = XGBClassifier(
                **(PARAMETERS | params)
            )

            model.fit(X_train, y_train)

            predicted_numeric = model.predict(X_val)

            predictions = np.array([
                INT_TO_LABEL[int(value)]
                for value in predicted_numeric
            ])

            macro_f1 = f1_score(
                y_val,
                predictions,
                labels=list(LABELS),
                average="macro",
                zero_division=0
            )

            accuracy = accuracy_score(y_val, predictions)

            high_recall = recall_score(
                y_val,
                predictions,
                labels=["high"],
                average="macro",
                zero_division=0
            )

            tuning_results.append({
                "feature_set": feature_set,
                "configuration": i + 1,
                **params,
                "accuracy": accuracy,
                "macro_f1": macro_f1,
                "high_severity_recall": high_recall
            })

            if macro_f1 > best_score:
                best_score = macro_f1
                best_models[feature_set] = model

    results_df = pd.DataFrame(tuning_results)

    results_df = results_df.sort_values(
        "macro_f1",
        ascending=False
    ).reset_index(drop=True)

    return results_df, best_models


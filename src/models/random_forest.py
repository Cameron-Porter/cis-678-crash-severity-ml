# Random Forest
import json
import platform
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import scipy
import sklearn

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from src.data.joins import CRASH_KEY, check_keys
from src.data.preprocess import sha256
from src.evaluation.evaluate import LABELS, evaluate_predictions


PARAMETERS = dict(
    n_estimators=100,
    criterion="gini",
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features="sqrt",
    class_weight=None,
    random_state=42,
    n_jobs=-1
)

def fit_random_forest_models(inputs, *, parameters=None):
    models = {}

    settings = PARAMETERS | (parameters or {})

    for configuration, item in inputs.items():
        matrix, rows = item["train"]

        check_keys(rows, CRASH_KEY, "training")

        if rows.empty or not rows.YEAR_FILE.isin([2020, 2021, 2022]).all():
            raise ValueError(
                "Fit Random Forest on 2020-2022 training rows only"
            )

        if set(rows.SEVERITY) != set(LABELS) or matrix.shape[0] != len(rows):
            raise ValueError(
                "Training requires all three severity classes and aligned rows"
            )

        model = RandomForestClassifier(**settings)

        model.fit(matrix, rows.SEVERITY)

        models[configuration] = model

    return models


def evaluate_random_forest_models(inputs, models):
    results = {}

    for configuration, model in models.items():
        matrix, rows = inputs[configuration]["validation"]

        check_keys(rows, CRASH_KEY, "validation")

        if rows.empty or not rows.YEAR_FILE.eq(2023).all():
            raise ValueError(
                "Evaluate Random Forest on 2023 validation only"
            )

        predicted = model.predict(matrix)

        metrics, per_class, confusion = evaluate_predictions(
            rows.SEVERITY, predicted
        )

        output = rows[CRASH_KEY].copy()
        output["y_true"] = rows.SEVERITY.to_numpy()
        output["y_pred"] = predicted

        probabilities = model.predict_proba(matrix)

        for label in LABELS:
            output[f"p_{label}"] = probabilities[
                :, list(model.classes_).index(label)
            ]

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

def save_random_forest_results(root, inputs, models, results):
    root = Path(root)

    report = root / "results" / "random_forest"
    local = root / "data/processed/predictions/random_forest"

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
        model="RandomForestClassifier",
        parameters={
            c: m.get_params()
            for c, m in models.items()
        },
        versions=dict(
            python=platform.python_version(),
            sklearn=sklearn.__version__,
            numpy=np.__version__,
            pandas=pd.__version__,
            scipy=scipy.__version__
        ),
        labels=list(LABELS),
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
                root / "src/models/random_forest.py",
                root / "src/models/data.py",
                root / "src/evaluation/evaluate.py"
            )
        }
    )

    (report / "run.json").write_text(
        json.dumps(run, indent=2, sort_keys=True) + "\n",
        encoding="utf8"
    )


from sklearn.metrics import f1_score, accuracy_score, recall_score

def tune_random_forest(inputs):

    configurations = [
        {"n_estimators": 100, "max_depth": None, "min_samples_leaf": 1, "class_weight": None},
        {"n_estimators": 100, "max_depth": None, "min_samples_leaf": 1, "class_weight": "balanced"},
        {"n_estimators": 100, "max_depth": 20, "min_samples_leaf": 1, "class_weight": "balanced"},
        {"n_estimators": 100, "max_depth": 20, "min_samples_leaf": 5, "class_weight": "balanced"},
        {"n_estimators": 100, "max_depth": 10, "min_samples_leaf": 5, "class_weight": "balanced"},
        {"n_estimators": 200, "max_depth": 20, "min_samples_leaf": 5, "class_weight": "balanced"},
        {"n_estimators": 200, "max_depth": 10, "min_samples_leaf": 5, "class_weight": "balanced"},
        {"n_estimators": 200, "max_depth": None, "min_samples_leaf": 5, "class_weight": "balanced"}
    ]

    tuning_results = []
    best_models = {}

    for feature_set in ["core", "expanded"]:

        X_train, train_rows = inputs[feature_set]["train"]
        X_val, val_rows = inputs[feature_set]["validation"]

        y_train = train_rows["SEVERITY"]
        y_val = val_rows["SEVERITY"]

        best_score = -1

        for i, params in enumerate(configurations):

            print(f"Training {feature_set}, configuration {i+1}/8...", flush=True)

            model = RandomForestClassifier(
                **params,
                random_state=42,
                n_jobs=-1
            )

            model.fit(X_train, y_train)

            predictions = model.predict(X_val)

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
import json
from pathlib import Path

import pandas as pd

from src.data.preprocess import sha256
from src.models.logistic_regression import fit_logistic_models, evaluate_logistic_models, save_logistic_results
from src.models.majority_baseline import fit_baselines, evaluate_baselines

C_VALUES = (0.01, 0.1, 1.0, 10.0, 100.0)
CLASS_WEIGHTS = (None, 'balanced')
SELECTION_RULE = 'Highest validation macro-F1; exact ties use smaller C, then unweighted, then core.'


def rank_candidates(metrics):
    return metrics.sort_values(['macro_f1', 'C', 'class_weight', 'configuration'],
                               ascending=[False, True, False, True], kind='stable')


def tune_baselines(inputs):
    candidates, per_class, confusion = [], [], []
    best_models, best_results, best_metrics = {}, {}, {}
    for C in C_VALUES:
        for weight in CLASS_WEIGHTS:
            models = fit_logistic_models(inputs, C=C, class_weight=weight)
            results = evaluate_logistic_models(inputs, models)
            for configuration, result in results.items():
                settings = dict(C=C, class_weight=weight or 'unweighted', configuration=configuration)
                metrics = result['metrics'] | settings
                candidates.append(metrics)
                per_class.append(result['per_class'].assign(**settings))
                confusion.append(result['confusion'].assign(**settings))
                previous = best_metrics.get(configuration)
                if previous is None or rank_candidates(pd.DataFrame([metrics, previous])).iloc[0].to_dict() == metrics:
                    best_metrics[configuration] = metrics
                    best_models[configuration] = models[configuration]
                    best_results[configuration] = result | {'metrics': metrics}
    ranked = rank_candidates(pd.DataFrame(candidates)).reset_index(drop=True)
    selected = pd.DataFrame(best_metrics.values())
    majority = evaluate_baselines(inputs, fit_baselines(inputs))
    comparison = pd.concat([
        pd.DataFrame([r['metrics'] for r in majority.values()]).assign(model='majority'),
        selected.assign(model='tuned_logistic_regression'),
    ], ignore_index=True)
    return dict(candidates=ranked, per_class=pd.concat(per_class, ignore_index=True),
                confusion=pd.concat(confusion, ignore_index=True), models=best_models,
                results=best_results, winner=ranked.iloc[0].to_dict(), comparison=comparison)


def save_tuning_results(root, inputs, tuning):
    root = Path(root)
    save_logistic_results(root, inputs, tuning['models'], tuning['results'], tuned=True)
    report = root / 'results/baseline_tuning'
    for name in ('candidates', 'per_class', 'confusion', 'comparison'):
        filename = f'candidate_{name}.csv' if name in ('per_class', 'confusion') else f'{name}.csv'
        tuning[name].to_csv(report / filename, index=False, lineterminator='\n')
    path = report / 'run.json'
    run = json.loads(path.read_text(encoding='utf8'))
    run['search'] = dict(C=list(C_VALUES), class_weight=list(CLASS_WEIGHTS), selection_rule=SELECTION_RULE,
                         winner=tuning['winner'], refit_on_validation=False)
    for relative in ('src/models/tune_baselines.py', 'src/models/majority_baseline.py'):
        run['source_hashes'][relative] = sha256(root / relative)
    path.write_text(json.dumps(run, indent=2, sort_keys=True)+'\n', encoding='utf8')

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

LABELS = ('low', 'moderate', 'high')


def evaluate_predictions(y_true, y_pred):
    actual, predicted = np.asarray(y_true), np.asarray(y_pred)
    if actual.ndim != 1 or predicted.ndim != 1 or len(actual) == 0 or len(actual) != len(predicted):
        raise ValueError('Expected matching nonempty one-dimensional labels')
    if not np.isin(actual, LABELS).all() or not np.isin(predicted, LABELS).all():
        raise ValueError('Evaluation requires known severity labels')
    precision, recall, f1, support = precision_recall_fscore_support(
        actual, predicted, labels=list(LABELS), zero_division=0)
    summary = {'accuracy': float(accuracy_score(actual, predicted)),
               'macro_f1': float(f1.mean()), 'high_severity_recall': float(recall[2])}
    per_class = pd.DataFrame({'label': LABELS, 'precision': precision, 'recall': recall,
                              'f1': f1, 'support': support})
    matrix = confusion_matrix(actual, predicted, labels=list(LABELS))
    confusion = pd.DataFrame([{'actual': a, 'predicted': p, 'rows': int(matrix[i, j])}
                              for i, a in enumerate(LABELS) for j, p in enumerate(LABELS)])
    return summary, per_class, confusion

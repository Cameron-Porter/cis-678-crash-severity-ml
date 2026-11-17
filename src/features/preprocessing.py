import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.validation import check_is_fitted

from src.features.build_features import (
    CORE_CATEGORICAL, CORE_NUMERIC, DRIVER_CATEGORICAL, DRIVER_NUMERIC,
    feature_columns, select_features,
)


class TrainingFeatureSelector(TransformerMixin, BaseEstimator):
    def __init__(self, configuration='core'):
        self.configuration = configuration

    def fit(self, X, y=None):
        select_features(X, self.configuration)
        if 'YEAR_FILE' not in X or X.empty or not X.YEAR_FILE.isin([2020, 2021, 2022]).all():
            raise ValueError('Fit preprocessing on 2020-2022 training rows only; YEAR_FILE is required')
        self.feature_names_out_ = np.asarray(feature_columns(self.configuration), dtype=object)
        return self

    def transform(self, X):
        check_is_fitted(self, 'feature_names_out_')
        return select_features(X, self.configuration).astype(float)

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self, 'feature_names_out_')
        return self.feature_names_out_.copy()


def make_preprocessor(configuration='core', *, scale_numeric=True):
    feature_columns(configuration)
    categorical = list(CORE_CATEGORICAL)
    numeric = list(CORE_NUMERIC)
    if configuration == 'expanded':
        categorical += list(DRIVER_CATEGORICAL)
        numeric += list(DRIVER_NUMERIC)
    categories = Pipeline([
        ('impute', SimpleImputer(strategy='constant', fill_value=-1, keep_empty_features=True)),
        ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=True)),
    ])
    numbers = Pipeline([
        ('impute', SimpleImputer(strategy='median', keep_empty_features=True)),
        ('scale', StandardScaler() if scale_numeric else 'passthrough'),
    ])
    return Pipeline([
        ('select', TrainingFeatureSelector(configuration)),
        ('columns', ColumnTransformer([
            ('categorical', categories, categorical), ('numeric', numbers, numeric),
        ], remainder='drop', sparse_threshold=1.0)),
    ])

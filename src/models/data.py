import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import load_npz

from src.data.joins import CRASH_KEY, check_keys
from src.data.preprocess import SPLIT_YEARS, sha256
from src.evaluation.evaluate import LABELS


def load_baseline_inputs(root):
    root = Path(root)
    inputs = {}
    for configuration in ('core', 'expanded'):
        folder = root / 'data/processed/features' / configuration
        metadata = json.loads((folder / 'metadata.json').read_text(encoding='utf8'))
        if metadata['configuration'] != configuration or metadata['fit_years'] != [2020, 2021, 2022]:
            raise ValueError('Feature configuration or fit years differ from the baseline contract')
        if metadata['processed_manifest_sha256'] != sha256(root / 'data/processed/manifest.json'):
            raise ValueError('Feature inputs are stale; rerun prepare_features.py')
        filenames = ['train.npz', 'validation.npz', 'train_rows.csv', 'validation_rows.csv', 'columns.csv']
        for filename in filenames:
            if sha256(folder / filename) != metadata['files'][filename]:
                raise ValueError(f'Feature artifact hash mismatch: {configuration}/{filename}')
        names = pd.read_csv(folder / 'columns.csv')['feature']
        if names.empty or names.isna().any() or names.duplicated().any():
            raise ValueError('Invalid encoded feature names')
        item = {'metadata': metadata, 'metadata_sha256': sha256(folder / 'metadata.json')}
        for split in ('train', 'validation'):
            rows = pd.read_csv(folder / f'{split}_rows.csv')
            matrix = load_npz(folder / f'{split}.npz').tocsr()
            check_keys(rows, CRASH_KEY, split)
            if rows.empty or set(rows.YEAR_FILE.unique()) != set(SPLIT_YEARS[split]):
                raise ValueError(f'{split}: incorrect years or empty data')
            if not rows.SEVERITY.isin(LABELS).all():
                raise ValueError(f'{split}: unknown or invalid labels')
            if matrix.shape != (len(rows), len(names)) or not np.isfinite(matrix.data).all():
                raise ValueError(f'{split}: invalid feature matrix')
            counts = metadata['exclusions'][split]
            if counts['eligible_rows'] != len(rows) or counts['input_rows'] != len(rows) + counts['excluded_unknown']:
                raise ValueError(f'{split}: exclusion counts do not match')
            item[split] = (matrix, rows)
        inputs[configuration] = item
    for split in ('train', 'validation'):
        pd.testing.assert_frame_equal(inputs['core'][split][1], inputs['expanded'][split][1])
    return inputs

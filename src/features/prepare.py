import json
import platform

import numpy as np
import scipy
from pathlib import Path
from tempfile import TemporaryDirectory

import joblib
import pandas as pd
import sklearn
from scipy.sparse import csr_matrix, save_npz

from src.data.joins import CRASH_KEY, check_keys
from src.data.load import read_raw_csv
from src.data.preprocess import SPLIT_YEARS, read_processed_csv, sha256
from src.features.build_features import SOURCE_COLUMNS, build_feature_table


def load_feature_split(root, split):
    root = Path(root)
    if split not in SPLIT_YEARS:
        raise ValueError('Expected train, validation, or test')
    path = root / 'data/processed' / f'{split}.csv'
    manifest = json.loads((path.parent / 'manifest.json').read_text(encoding='utf8'))
    if sha256(path) != manifest['outputs'][path.name]['sha256']:
        raise ValueError('Processed data differs from its build manifest; rebuild data first')
    schema = pd.read_csv(root / 'docs/crss_processed_schema.csv')
    crashes = read_processed_csv(path, schema)
    check_keys(crashes, CRASH_KEY, split)
    if set(crashes.YEAR_FILE.unique()) != set(SPLIT_YEARS[split]):
        raise ValueError('Processed split has incorrect years')
    if not crashes.SEVERITY.isin(['low', 'moderate', 'high', 'unknown']).all():
        raise ValueError('Unexpected target label')
    tables = {}
    for table in ('vehicle', 'person'):
        frames = []
        for year in SPLIT_YEARS[split]:
            raw = root / 'data/raw' / str(year) / f'{table}.csv'
            if sha256(raw) != manifest['inputs'][raw.relative_to(root).as_posix()]:
                raise ValueError('Raw data differs from processed-data inputs; rebuild data first')
            columns = [c for c in SOURCE_COLUMNS[table] if c != 'YEAR_FILE']
            frames.append(read_raw_csv(raw, usecols=columns).assign(YEAR_FILE=year))
        tables[table] = pd.concat(frames, ignore_index=True)
    features = build_feature_table(crashes, **tables)
    pd.testing.assert_frame_equal(features[CRASH_KEY].reset_index(drop=True), crashes[CRASH_KEY].reset_index(drop=True))
    eligible = crashes.SEVERITY.ne('unknown')
    counts = {'input_rows': len(crashes), 'excluded_unknown': int((~eligible).sum()), 'eligible_rows': int(eligible.sum())}
    return features.loc[eligible].reset_index(drop=True), crashes.loc[eligible, 'SEVERITY'].reset_index(drop=True), counts


def save_feature_artifacts(root, configuration, preprocessor, frames, targets, matrices, exclusions):
    root = Path(root)
    if set(frames) != {'train', 'validation'}:
        raise ValueError('This preparation workflow exports train and validation only')
    if preprocessor.named_steps['select'].configuration != configuration:
        raise ValueError('Configuration differs from fitted preprocessor')
    names = preprocessor.get_feature_names_out()
    out = root / 'data/processed/features' / configuration
    out.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=out, prefix='build-') as directory:
        temporary = Path(directory)
        for split, frame in frames.items():
            matrix = csr_matrix(matrices[split])
            if matrix.shape != (len(frame), len(names)) or len(targets[split]) != len(frame):
                raise ValueError('Feature matrix, names, and target rows do not align')
            check_keys(frame, CRASH_KEY, split)
            if not frame.index.equals(targets[split].index):
                raise ValueError('Target index does not match feature rows')
            if not targets[split].isin(['low', 'moderate', 'high']).all():
                raise ValueError('Export only known severity targets')
            if not frame.YEAR_FILE.isin(SPLIT_YEARS[split]).all() or not np.isfinite(matrix.data).all():
                raise ValueError('Invalid split years or nonfinite transformed values')
            rows = frame[CRASH_KEY].reset_index(drop=True).copy()
            rows['SEVERITY'] = targets[split].to_numpy()
            rows.to_csv(temporary / f'{split}_rows.csv', index=False)
            save_npz(temporary / f'{split}.npz', matrix)
        pd.DataFrame({'feature': names}).to_csv(temporary / 'columns.csv', index=False)
        joblib.dump(preprocessor, temporary / 'preprocessor.joblib')
        files = {p.name: sha256(p) for p in temporary.iterdir()}
        metadata = {'configuration': configuration, 'sklearn': sklearn.__version__,
                    'pandas': pd.__version__, 'numpy': np.__version__, 'scipy': scipy.__version__,
                    'python': platform.python_version(), 'fit_years': [2020, 2021, 2022],
                    'scale_numeric': preprocessor.named_steps['columns'].named_transformers_['numeric'].named_steps['scale'] != 'passthrough',
                    'exclusions': exclusions, 'files': files,
                    'processed_manifest_sha256': sha256(root / 'data/processed/manifest.json'),
                    'source_hashes': {p.relative_to(root).as_posix(): sha256(p)
                                      for p in sorted((root / 'src/features').glob('*.py'))}}
        (temporary / 'metadata.json').write_text(json.dumps(metadata, indent=2, sort_keys=True)+'\n', encoding='utf8')
        for p in temporary.iterdir():
            p.replace(out / p.name)

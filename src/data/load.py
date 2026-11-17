"""Read CRSS CSVs without turning valid text categories into missing values."""

import csv
from pathlib import Path

import pandas as pd


def read_raw_csv(path, *, text=False, usecols=None):
    """Preserve literal 'None' and 'NA'; only empty CSV cells become nulls."""
    path = Path(path)
    with path.open(encoding="latin-1", newline="") as stream:
        columns = [name.upper() for name in next(csv.reader(stream))]
    if len(columns) != len(set(columns)):
        raise ValueError(f"Column names collide after uppercasing: {path}")
    frame = pd.read_csv(path, encoding="latin-1", low_memory=False,
                        keep_default_na=False, na_values=[""], dtype="string" if text else None,
                        usecols=usecols)
    frame.columns = frame.columns.str.upper()
    return frame

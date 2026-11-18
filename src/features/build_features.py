import numpy as np
import pandas as pd

from src.data.joins import CRASH_KEY, audit_raw_joins, merge_crash_summary

CORE_CATEGORICAL = ("MONTH", "DAY_WEEK", "HOUR", "TYP_INT", "INT_HWY", "LGT_COND", "WEATHER")
CORE_NUMERIC = ("VE_TOTAL", "VEHICLE_AGE_MIN", "VEHICLE_AGE_MAX")
DRIVER_CATEGORICAL = ("SPEEDING_ANY", "DRINKING_ANY")
DRIVER_NUMERIC = ("DRIVER_AGE_MIN", "DRIVER_AGE_MAX")
CORE_FEATURES = CORE_CATEGORICAL + CORE_NUMERIC
EXPANDED_FEATURES = CORE_FEATURES + DRIVER_CATEGORICAL + DRIVER_NUMERIC

SOURCE_COLUMNS = {
    "accident": ("CASENUM", "YEAR_FILE", *CORE_CATEGORICAL, "VE_TOTAL"),
    "vehicle": ("CASENUM", "YEAR_FILE", "VEH_NO", "MOD_YEAR", "SPEEDREL"),
    "person": ("CASENUM", "YEAR_FILE", "VEH_NO", "PER_NO", "PER_TYP", "AGE", "DRINKING"),
}


def feature_columns(configuration):
    if configuration == "core":
        return CORE_FEATURES
    if configuration == "expanded":
        return EXPANDED_FEATURES
    raise ValueError("configuration must be 'core' or 'expanded'")


def select_features(frame, configuration):
    columns = feature_columns(configuration)
    if frame.columns.duplicated().any():
        raise ValueError("Duplicate feature-table columns")
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing constructed features: {sorted(missing)}")
    return frame.loc[:, list(columns)].copy()



CATEGORY_CODES = {
    "MONTH": (set(range(1, 13)), set()),
    "DAY_WEEK": (set(range(1, 8)), {9}),
    "HOUR": (set(range(24)), {99}),
    "TYP_INT": ({1, 2, 3, 4, 5, 6, 7, 10, 11}, {98, 99}),
    "INT_HWY": ({0, 1}, {9}),
    "LGT_COND": (set(range(1, 8)), {8, 9}),
    "WEATHER": ({1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12}, {98, 99}),
}


def numeric_values(values, name):
    blanks = values.isna() | values.astype('string').str.strip().eq('').fillna(False)
    numeric = pd.to_numeric(values.mask(blanks), errors='coerce').astype(float)
    if ((~blanks & numeric.isna()) | (numeric.notna() & (~np.isfinite(numeric) | numeric.mod(1).ne(0)))).any():
        raise ValueError(f'{name}: expected integer codes or blanks')
    return numeric


def clean_codes(values, valid, missing, name):
    numeric = numeric_values(values, name)
    if (numeric.notna() & ~numeric.isin(valid | missing)).any():
        raise ValueError(f'{name}: unexpected code')
    return numeric.mask(numeric.isin(missing))


def age_summary(frame, values, prefix):
    work = frame[CRASH_KEY].copy()
    work['value'] = values
    return work.groupby(CRASH_KEY)['value'].agg(['min', 'max']).rename(
        columns={'min': prefix + '_MIN', 'max': prefix + '_MAX'}).reset_index()


def behavior_summary(frame, values, positive_codes, name):
    work = frame[CRASH_KEY].copy()
    work['positive'] = values.isin(positive_codes)
    work['negative'] = values.eq(0)
    grouped = work.groupby(CRASH_KEY).agg(positive=('positive', 'any'), negative=('negative', 'all'))
    grouped[name] = np.where(grouped.positive, 1.0, np.where(grouped.negative, 0.0, np.nan))
    return grouped[[name]].reset_index()


def build_feature_table(crashes, vehicle, person):
    for name, frame in [('accident', crashes), ('vehicle', vehicle), ('person', person)]:
        if frame.columns.duplicated().any():
            raise ValueError(f'{name}: duplicate columns')
        missing = set(SOURCE_COLUMNS[name]) - set(frame)
        if missing:
            raise ValueError(f'{name}: missing source columns {sorted(missing)}')
    audit_raw_joins(crashes, vehicle, person)
    if not crashes.YEAR_FILE.isin(range(2020, 2025)).all():
        raise ValueError('Unreviewed source year')
    result = crashes[CRASH_KEY].copy()
    for name, (valid, missing) in CATEGORY_CODES.items():
        result[name] = clean_codes(crashes[name], valid, missing, name)
    result['VE_TOTAL'] = clean_codes(crashes.VE_TOTAL, set(range(1, 1000)), set(), 'VE_TOTAL')

    model_year = numeric_values(vehicle.MOD_YEAR, 'MOD_YEAR').replace([9998, 9999], np.nan)
    if (model_year.notna() & (~model_year.ge(1886) | ~model_year.le(vehicle.YEAR_FILE + 1))).any():
        raise ValueError('MOD_YEAR: outside reviewed range')
    ages = (vehicle.YEAR_FILE - model_year).clip(lower=0)
    result = merge_crash_summary(result, age_summary(vehicle, ages, 'VEHICLE_AGE'))

    # Driver identity comes from PER_TYP, never person order or injury severity.
    roles = numeric_values(person.PER_TYP, 'PER_TYP')
    drivers = person.loc[roles.eq(1)]
    driver_age = clean_codes(drivers.AGE, set(range(121)), {998, 999}, 'AGE')
    result = merge_crash_summary(result, age_summary(drivers, driver_age, 'DRIVER_AGE'))
    speeding = clean_codes(vehicle.SPEEDREL, {0, 2, 3, 4, 5}, {8, 9}, 'SPEEDREL')
    result = merge_crash_summary(result, behavior_summary(vehicle, speeding, {2, 3, 4, 5}, 'SPEEDING_ANY'))
    drinking = clean_codes(drivers.DRINKING, {0, 1}, {8, 9}, 'DRINKING')
    result = merge_crash_summary(result, behavior_summary(drivers, drinking, {1}, 'DRINKING_ANY'))
    return result[CRASH_KEY + list(EXPANDED_FEATURES)]

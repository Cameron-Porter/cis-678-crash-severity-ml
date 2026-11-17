
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

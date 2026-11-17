"""Check CRSS keys and join crash summaries without changing the crash count."""

import pandas as pd


CRASH_KEY = ["YEAR_FILE", "CASENUM"]
VEHICLE_KEY = CRASH_KEY + ["VEH_NO"]
PERSON_KEY = VEHICLE_KEY + ["PER_NO"]


def check_keys(frame, keys, name):
    """Stop on missing or repeated keys instead of silently dropping records."""
    if frame[keys].isna().any().any():
        raise ValueError(f"{name}: missing key values")
    if frame.duplicated(keys).any():
        raise ValueError(f"{name}: duplicate keys {keys}")


def unmatched_rows(child, parent, keys):
    """Return child rows with no matching parent key."""
    parent_keys = pd.MultiIndex.from_frame(parent[keys])
    return ~pd.MultiIndex.from_frame(child[keys]).isin(parent_keys)


def audit_raw_joins(accident, vehicle, person):
    """Validate raw keys and report coverage per year, without dropping records."""
    for frame, keys, name in (
        (accident, CRASH_KEY, "accident"),
        (vehicle, VEHICLE_KEY, "vehicle"),
        (person, PERSON_KEY, "person"),
    ):
        check_keys(frame, keys, name)
    for frame, name in ((vehicle, "vehicle"), (person, "person")):
        if unmatched_rows(frame, accident, CRASH_KEY).any():
            raise ValueError(f"{name}: records without a matching accident")

    records = []
    for year in sorted(accident["YEAR_FILE"].unique()):
        a = accident.loc[accident.YEAR_FILE.eq(year)]
        v = vehicle.loc[vehicle.YEAR_FILE.eq(year)]
        p = person.loc[person.YEAR_FILE.eq(year)]
        # VEH_NO=0 has no vehicle link. Keep these people in crash summaries.
        vehicle_people = p.loc[p.VEH_NO.ne(0)]
        records.append({
            "year": year, "accident_rows": len(a), "vehicle_rows": len(v),
            "person_rows": len(p),
            "crashes_with_vehicles": len(a) - int(unmatched_rows(a, v, CRASH_KEY).sum()),
            "crashes_without_vehicles": int(unmatched_rows(a, v, CRASH_KEY).sum()),
            "crashes_with_people": len(a) - int(unmatched_rows(a, p, CRASH_KEY).sum()),
            "crashes_without_people": int(unmatched_rows(a, p, CRASH_KEY).sum()),
            "people_with_vehicle_no_zero": int(p.VEH_NO.eq(0).sum()),
            "people_without_matching_vehicle": int(unmatched_rows(vehicle_people, v, VEHICLE_KEY).sum()),
        })
    return pd.DataFrame(records)


def merge_crash_summary(crashes, summary):
    """Left join a unique crash summary and keep every original crash exactly once."""
    check_keys(crashes, CRASH_KEY, "left crash table")
    check_keys(summary, CRASH_KEY, "crash summary")
    if unmatched_rows(summary, crashes, CRASH_KEY).any():
        raise ValueError("Crash summary contains keys absent from the left crash table")
    overlap = (set(crashes) & set(summary)) - set(CRASH_KEY)
    if overlap:
        raise ValueError(f"Summary columns already exist: {sorted(overlap)}")
    result = crashes.merge(summary, on=CRASH_KEY, how="left", validate="one_to_one")
    check_keys(result, CRASH_KEY, "joined crashes")
    if len(result) != len(crashes) or unmatched_rows(crashes, result, CRASH_KEY).any():
        raise ValueError("Crash keys or record count changed during the join")
    return result

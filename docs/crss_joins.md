# Crash-level joins

We keep one row per crash using `YEAR_FILE` and `CASENUM`. The notebook groups
person and vehicle records by these keys before attaching severity to the
accident table. This avoids multiplying rows when a crash has several vehicles
or people.

The shared checks are in `src/data/joins.py`. Run the preprocessing notebook
from `notebooks/` to use them and update [the join report](crss_join_audit.csv).
The report uses our local raw files and includes the final crash count by year.

## Checks before joining

- Accident keys: `YEAR_FILE`, `CASENUM`.
- Vehicle keys: `YEAR_FILE`, `CASENUM`, `VEH_NO`.
- Person keys: `YEAR_FILE`, `CASENUM`, `VEH_NO`, `PER_NO`.

Missing or duplicate keys stop the notebook. Vehicle and person records must
also have a matching accident. These checks run before grouping, so aggregation
cannot hide duplicate input records.

We check person-to-vehicle coverage using the vehicle key. People with
`VEH_NO = 0` are counted separately because they have no vehicle link. Other
unmatched vehicle keys are reported, not dropped. Every person still contributes
to the summary for their crash. The report does not establish why a vehicle
link is missing; check the source records and manuals before using those links
for vehicle or driver features.

## Checks during joining

Both summary joins use pandas' `one_to_one` validation. The final join starts
from the accident table and keeps every original crash key. Duplicate summary
keys, unexpected crash keys, overlapping columns, or changed crash counts stop
the join. The notebook also compares the before/after counts for each year.

The injury summary only contains crashes with person records. Crashes without
people are kept by the final left join and retain the notebook's `unknown`
label. This issue adds join checks; severity rules remain DATA-03.

## Current data

All five years pass the raw-key checks. Every crash has vehicle records.
The report lists crashes without people and people without matching vehicles
by year. These gaps are kept visible rather than removed by an inner join.

The final table has 264,661 crashes: 162,900 from 2020–2022, 50,103 from 2023,
and 51,658 from 2024. There are 81 crashes without person records.

Run the focused tests from the repository root:

```bash
python -m unittest discover -s tests -p test_data_joins.py -v
```

On macOS, use `python3`. The tests cover repeated crash numbers across years,
missing matches, duplicate or missing keys, and records without a parent crash.

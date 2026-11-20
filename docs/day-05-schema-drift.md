# Day 5: CSV Schema Drift Detector

## Purpose

Compare a baseline CSV with a current CSV and produce a JSON report of
structural and data-quality changes.

## Findings

- `added_column`: a new column exists in the current CSV (medium severity).
- `removed_column`: a baseline column is missing (high severity).
- `type_changed`: an existing column's inferred type changed (high severity).
- `missing_rate_increased`: blank values increased by the configured threshold
  or more (medium severity).

Types are inferred from nonblank values. Supported types are boolean, integer,
number, string, mixed, and unknown. Type inference is a useful heuristic, not a
replacement for an explicit business schema.

## Run the example

From the repository root with the project virtual environment activated:

```powershell
python -m dslab.drift --baseline data/day-05/baseline_customers.csv --current data/day-05/current_customers.csv --config configs/day-05-drift-config.json --output reports/day-05/drift_report.json
```

Exit codes: `0` means no drift was found, `1` means findings were reported, and
`2` means the command could not process its inputs or configuration. A report
is written when comparison succeeds, including when drift is found.

## Threshold

`missing_rate_increase_threshold` is a proportion from greater than zero through
one. The default is `0.2`, meaning a rise of 20 percentage points. Use
`--threshold 0.1` to override the config for a particular run.

## Limitations

Type inference uses values observed in each file and can be affected by small
samples, identifiers with leading zeroes, date strings, and mixed data. Review
high-severity findings before changing a production pipeline.

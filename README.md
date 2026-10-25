
## Day 4: Configurable Validation Rules Engine

Day 4 adds configurable CSV validation using JSON rules. It supports required
fields, type checks, numeric ranges, allowed values, string lengths, unique
fields, and machine-readable JSON reports.

See [the Day 4 guide](docs/day-04-validation-rules.md) for setup and usage.

## Day 5: CSV Schema Drift Detector

Compare baseline and current CSV datasets to identify added or removed columns,
inferred type changes, and increases in missing values. The command writes a
JSON report with severity levels.

Run:

```powershell
python -m dslab.drift --baseline data/day-05/baseline_customers.csv --current data/day-05/current_customers.csv --config configs/day-05-drift-config.json --output reports/day-05/drift_report.json
```

See `docs/day-05-schema-drift.md` for details and exit codes.


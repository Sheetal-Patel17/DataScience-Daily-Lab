
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

## Day 6: Unified Data Quality Scorecard

Calculate a weighted 0–100 score using completeness, uniqueness, and validity.
The report includes quality grades, metric counts, and recommendations.

```powershell
python -m dslab.scorecard --input data/day-06/customers.csv --config configs/day-06-scorecard.json --output reports/day-06/scorecard.json
```

See `docs/day-06-data-quality-scorecard.md` for the scoring methodology.


## Day 7: Distribution Drift Detection

Compare baseline and current CSV datasets to flag possible shifts in numeric
and categorical distributions and missing-value rates. The JSON report includes
per-column signals, configured thresholds, and schema differences.

```powershell
python -m dslab.distribution_drift --baseline data/day-07/baseline_customers.csv --current data/day-07/current_customers.csv --config configs/day-07-distribution-drift.json --output reports/day-07/distribution-drift.json
```

See [the Day 7 guide](docs/day-07-distribution-drift.md) for methodology,
thresholds, usage, and limitations.

## Day 8: Dataset Provenance and Integrity Audit

Create SHA-256 provenance manifests for input CSVs and optional JSON configs,
record dataset shape and runtime details, then verify later that source contents
still match the recorded snapshot.

```powershell
python -m dslab.provenance create --input data/day-08/orders_snapshot.csv --config configs/day-08-provenance.json --output reports/day-08/provenance-manifest.json
python -m dslab.provenance verify --manifest reports/day-08/provenance-manifest.json --output reports/day-08/verification.json
```

See [the Day 8 guide](docs/day-08-provenance-audit.md) for usage and limitations.
# DataScience-Daily-Lab

A hands-on data science and data quality toolkit built through daily practical projects, with examples, tests, and documentation.

## Day 1: Data Quality Toolkit

Built a foundational toolkit for CSV profiling, missing-value and duplicate detection, JSON reporting, SQL data-quality checks, and an R example. Added automated tests, linting, and continuous integration.

## Day 2: Data Cleaning Pipeline

Built a repeatable CSV cleaning workflow that separates valid records from rejected records and generates a quality report. Outputs include `customers_clean.csv`, `customers_rejected.csv`, and `quality_report.json`.

## Day 3: HTML Data Profile

Created an HTML data profiling tool to make dataset structure and quality easier to inspect through a readable report.

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

Calculate a weighted 0Ã¢â‚¬â€œ100 score using completeness, uniqueness, and validity.
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
## Day 9: Dataset Splitter and Leakage Guard

Create reproducible train, validation, and test CSVs with optional target
stratification and group-aware splitting. The JSON report summarizes split
ratios and warns when exact duplicate rows cross partitions.

```powershell
python -m dslab.dataset_split --input data/day-09/orders_labeled.csv --config configs/day-09-split.json --output-dir reports/day-09/splits --group-column customer_id
```

See [the Day 9 guide](docs/day-09-dataset-split.md) for usage and limitations.

## Day 10: Classification Metrics Evaluator

Evaluate actual and predicted labels from a CSV using accuracy, per-class
precision/recall/F1, macro and weighted averages, and a confusion matrix.

```powershell
python -m dslab.classification_eval --input data/day-10/candidate_predictions.csv --output reports/day-10/candidate-evaluation.json
```

See [the Day 10 guide](docs/day-10-classification-evaluation.md) for metrics,
input requirements, and interpretation notes.

## Day 11: Model Evaluation Regression Guard

Compare baseline and candidate classification reports, then flag metric drops
that exceed configurable absolute thresholds.

```powershell
python -m dslab.evaluation_compare --baseline reports/day-10/baseline-evaluation.json --candidate reports/day-10/candidate-evaluation.json --config configs/day-11-regression-thresholds.json --output reports/day-11/evaluation-comparison.json
```

See [the Day 11 guide](docs/day-11-evaluation-regression-guard.md) for thresholds,
exit codes, and limitations.

## Day 12: Classification Slice Performance Audit

- Added classification metrics by group.
- Added minimum group-size checks.
- Added accuracy-gap warnings.
- Added per-class performance reporting.
- Documented the limitations of group comparisons.

## Day 13: Dataset Contamination and Duplicate Audit

Added a standard-library CSV audit tool to flag normalized duplicate rows,
overlap between two datasets, blank values, and suspicious target-related column
names. It generates a JSON report and includes automated tests, sample data, and
documented limitations.

Run:

```powershell
$env:PYTHONPATH = "src"
python -m dslab.contamination_report --input data/day-13/train.csv --compare data/day-13/test.csv --output reports/day-13-audit.json
```


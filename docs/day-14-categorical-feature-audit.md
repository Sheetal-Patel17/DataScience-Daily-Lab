# Day 14: Categorical Feature Audit

The categorical feature audit summarizes value frequencies and highlights areas
that may need review before machine-learning training.

## Run it

From the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m dslab.categorical_audit --input data/day-14/customers.csv --output reports/day-14/categorical-audit.json
```

Optional thresholds:

```powershell
python -m dslab.categorical_audit --input data/day-14/customers.csv --rare-threshold 0.05 --high-cardinality-threshold 0.50
```

## What it reports

- Value counts and unique-value cardinality per column.
- Blank values.
- Rare categories below the configured fraction of all rows.
- High-cardinality review signals.
- Values that normalize to the same text after case and whitespace cleanup.
- A JSON report with threshold settings and limitations.

## Important limitations

A high-cardinality column is not automatically an identifier. Rare categories may
be valid, and capitalization differences may be meaningful in some domains.
Review the flags in context rather than automatically dropping or rewriting data.

## Overall summary

The JSON report includes an overall summary in addition to per-column results:

- `columns_audited`: total number of columns inspected.
- `columns_needing_review`: columns with one or more review flags.
- `columns_without_flags`: columns with no review flags.
- `total_review_flags`: total number of flags across all columns.
- `flag_counts`: count of each review-flag type.

A column may have multiple flags, so the total number of flags can be greater
than the number of columns needing review.
## CSV input validation

The reader rejects empty files, blank column names, column names with
surrounding whitespace, duplicate column names, rows with missing or extra
fields, and unterminated quoted fields. Blank data records are preserved
so they can be counted during the audit.

# Day 7: Distribution Drift Detection

## Purpose

Compare a baseline CSV with a newer CSV and flag possible shifts in numeric
and categorical distributions, as well as changes in missing-value rates.
This complements Day 5 schema drift detection: schema drift focuses on columns
and inferred types, while this tool compares values within shared columns.

## Run

From the repository root:

```powershell
python -m dslab.distribution_drift --baseline data/day-07/baseline_customers.csv --current data/day-07/current_customers.csv --config configs/day-07-distribution-drift.json --output reports/day-07/distribution-drift.json
```

The command prints a status summary and writes a JSON report.

## How it works

- **Missing values:** compares the absolute difference between missing-value rates.
- **Numeric columns:** compares means and population standard deviations using relative changes.
- **Categorical columns:** uses total variation distance between observed category proportions.
- **Thresholds:** are configured in `configs/day-07-distribution-drift.json`.
- **Schema differences:** added and removed columns are listed but not distribution-compared.

A column is flagged when its missing-rate change or distribution change exceeds
the configured threshold. Threshold comparisons use a strict greater-than test.

## Report fields

The JSON report includes overall status, row counts, shared columns compared,
columns with drift, added and removed columns, thresholds, per-column metrics,
and limitations.

## Limitations

This is a screening tool, not proof of model degradation or a causal explanation.
Mean and standard-deviation comparisons can miss some numeric distribution
changes. Categorical comparisons consider observed values only. Review flagged
columns in context before taking action.
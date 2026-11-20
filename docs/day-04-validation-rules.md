# Day 4 — Configurable Validation Rules Engine

## Purpose

The Day 4 validation engine checks tabular data against a JSON configuration.
It reports issues without silently changing or deleting source records.

## Supported checks

- Required fields
- String, integer, number, and boolean types
- Numeric minimum and maximum
- Allowed values
- Minimum and maximum string length
- Unique field values

## Run it

Activate the project's virtual environment, then run this command from the
repository root:

```powershell
python -m dslab.validation `
  --input data/day-04/sample_customers.csv `
  --rules configs/day-04-validation-rules.json `
  --output reports/day-04/validation_report.json
```

The example intentionally contains invalid records, so the command returns
exit code `1` when validation issues are found. The JSON report is still
written and includes row counts and individual issues. A valid dataset returns
exit code `0`.

## How to customize the rules

Edit `configs/day-04-validation-rules.json`. The rule configuration controls
the fields and constraints; the validation code does not need to be changed
for ordinary rule updates.

CSV row numbers in the report are **data-row numbers**, starting at 1 after
the header. Duplicate checks flag the later occurrence and retain the first
occurrence's row number in the message.

This is a data-quality utility, not a substitute for business approval of
validation requirements.

# Day 6: Unified Data Quality Scorecard

## Purpose

Produce a score from 0 to 100 summarizing completeness, uniqueness, and validity. The JSON output includes component scores, grade, counts, and actionable recommendations.

## Scoring methodology

- **Completeness:** Percentage of cells that are not blank.
- **Uniqueness:** Percentage of rows that are not duplicate occurrences.
- **Validity:** Percentage of rows that pass required-field and configured numeric-range checks.
- **Overall score:** Weighted average of the three percentages, normalized by the sum of configured weights.

Default weights are 40% completeness, 30% uniqueness, and 30% validity. Grades are configurable in `configs/day-06-scorecard.json`.

## Run the scorecard

From the repository root, run:

```powershell
python -m dslab.scorecard --input data/day-06/customers.csv --config configs/day-06-scorecard.json --output reports/day-06-scorecard.json
```

Review the generated JSON report for the overall score, individual metrics, and recommendations.

## Important limitations

The validity score measures only the checks declared in the configuration. A numeric field that is blank is counted as incomplete; required fields also affect row validity. Duplicate detection compares complete rows, not a business key. This scorecard is a useful screening metric, not a guarantee that a dataset is correct or suitable for every business purpose.

## Troubleshooting

- **Configuration file not found:** Run the command from the repository root and check that `configs/day-06-scorecard.json` exists.
- **Input CSV not found:** Verify the CSV path and ensure the file is readable.
- **Invalid configuration:** Check that the JSON is valid and its scoring weights and column rules follow the configured schema.
- **Unexpected quality score:** Review the completeness, uniqueness, and validity metrics before changing the weights.
- **Test failures:** Run `python -m pytest -q` from the repository root to identify the failing test.

## Validation checklist

Before sharing a scorecard report:

1. Confirm that the input dataset is the intended version.
2. Review the individual quality metrics as well as the overall score.
3. Check recommendations against the actual data issues.
4. Keep the generated report with its configuration so the results can be reproduced.
# Day 6: Unified Data Quality Scorecard

## Purpose

Produce a score from 0 to 100 summarizing completeness, uniqueness, and
validity. The JSON output includes the component scores, grade, counts, and
actionable recommendations.

## Scoring methodology

- **Completeness:** percentage of cells that are not blank.
- **Uniqueness:** percentage of rows that are not duplicate occurrences.
- **Validity:** percentage of rows that pass required-field and configured
  numeric-range checks.
- **Overall score:** weighted average of those three percentages, normalized
  by the sum of configured weights.

Default weights are 40% completeness, 30% uniqueness, and 30% validity.
Grades are configurable in `configs/day-06-scorecard.json`.

## Run

```powershell
python -m dslab.scorecard --input data/day-06/customers.csv --config configs/day-06-scorecard.json --output reports/day-06/scorecard.json
```

## Important limitations

The validity score measures only the checks declared in the configuration.
A numeric field that is blank is counted as incomplete; required fields also
affect row validity. Duplicate detection compares complete rows, not a business
key. This scorecard is a useful screening metric, not a guarantee that a dataset
is correct or suitable for every business purpose.

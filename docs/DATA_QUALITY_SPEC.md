# Data Quality Specification — Day 1

## Purpose

Detect common CSV issues before a dataset enters an analytical workflow.

## Checks

| Check | Definition |
|---|---|
| Row count | Number of data records excluding the header |
| Column count | Number of uniquely named columns |
| Missing values | Empty or whitespace-only cells |
| Duplicate rows | Repeated complete rows after their first occurrence |
| Type inference | Simple integer, numeric, string, or empty classification |
| Quality status | Needs review if missing or duplicate cells are detected |

## Assumptions

- The input is a comma-separated UTF-8 text file.
- The first row contains column names.
- Column type inference is intentionally basic.
- Missing values are empty strings or whitespace-only strings.
- Duplicate rows are defined by equality across every column.

## Limitations

- Type inference does not validate dates or business-specific rules.
- CSV values such as "NULL" are not automatically treated as missing.
- The toolkit loads the full file into memory.
- A clean report does not prove that the data is accurate.
- Duplicate customer IDs are different from duplicate complete rows.

## Next improvements

1. Add configurable missing-value tokens.
2. Add date and schema validation.
3. Support large files through streaming.
4. Add machine-readable exit codes for quality failures.
5. Add SQL integration tests against a local database.

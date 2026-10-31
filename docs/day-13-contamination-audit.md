# Day 13 ? Dataset Contamination and Duplicate Audit

## Purpose

Screen CSV datasets for exact duplicate records, normalized duplicates, overlap
between two files, blank values, and column names that deserve target-leakage review.

## Run it

```powershell
$env:PYTHONPATH = "src"
python -m dslab.contamination_report --input data/day-13/train.csv --compare data/day-13/test.csv --output reports/day-13-audit.json
```

## Checks

- Duplicate rows are compared after trimming whitespace and normalizing case.
- Cross-file overlap is checked using the columns shared by both files.
- Suspicious names such as `target`, `label`, `outcome`, and `prediction` are
  flagged for manual review.
- Blank values are counted and included as an informational finding.
- The report is JSON and contains counts, severity labels, and short examples.

## Limitations

This is a screening tool, not a proof of data leakage. Similar records can be
legitimate. Column names can be misleading. It does not detect semantic duplicates,
time leakage, target-derived values hidden in arbitrary columns, or all forms of
entity overlap. Review findings in the context of how the dataset was collected
and split. Do not use these results alone to claim model fairness or validity.

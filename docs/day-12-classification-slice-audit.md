# Day 12 - Classification Slice Performance Audit

## Objective
Evaluate classification performance separately across groups such as region, device, or customer segment.

## Metrics
- Accuracy
- Macro precision, recall, and F1
- Weighted precision, recall, and F1
- Per-class metrics

Groups below the minimum sample size are marked insufficient_data.

## Run
Set PYTHONPATH to src and run the classification_slice_audit module with the sample CSV and region slice column.

## Limitations
Group differences are descriptive, not causal. Small groups may have unstable metrics. This audit alone does not establish fairness or prove model bias.

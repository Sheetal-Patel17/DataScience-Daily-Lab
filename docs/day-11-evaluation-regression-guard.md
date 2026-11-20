# Day 11: Model Evaluation Regression Guard

## Purpose

Compare a baseline evaluation report with a candidate report and flag drops in
accuracy, macro precision, macro recall, macro F1, or weighted F1 that exceed
configured thresholds. Thresholds are absolute score drops on the 0-to-1 scale.
For example, `0.03` means a three-percentage-point drop is allowed before an
accuracy regression is flagged.

## Run

First create evaluation reports using the Day 10 CLI, then compare them:

```powershell
python -m dslab.evaluation_compare --baseline reports/day-10/baseline-evaluation.json --candidate reports/day-10/candidate-evaluation.json --config configs/day-11-regression-thresholds.json --output reports/day-11/evaluation-comparison.json
```

Exit codes: `0` means no configured threshold was exceeded, `1` means one or
more metric regressions were detected, and `2` means the inputs/configuration
could not be processed. A regression result is an expected analytical finding,
not a program crash.

## Threshold configuration

Edit `metric_drop_thresholds` in `configs/day-11-regression-thresholds.json`.
Each metric accepts a number from 0 to 1. Unspecified metrics use the tool's
default thresholds. Unknown metric names, booleans, non-numeric values, and
out-of-range thresholds are rejected.

## Limitations

The guard assumes higher metric values are better and both reports use the same
evaluation dataset and methodology. It does not assess statistical uncertainty,
class imbalance outside the listed metrics, subgroup fairness, or data leakage.
Review evaluation datasets and model changes before deciding to ship a model.

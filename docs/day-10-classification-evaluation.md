# Day 10: Classification Metrics Evaluator

## Purpose

Calculate common single-label classification metrics from a CSV containing
known labels and model predictions. The tool uses only the Python standard
library so it can run without pandas or scikit-learn.

## Input format

The CSV must contain `actual_label` and `predicted_label` columns. Override
these names with `--actual-column` and `--predicted-column` when needed. Blank
labels, duplicate headers, extra row fields, and empty datasets are rejected.

## Run

```powershell
python -m dslab.classification_eval --input data/day-10/candidate_predictions.csv --output reports/day-10/candidate-evaluation.json
```

The JSON report contains accuracy, macro and weighted precision/recall/F1,
per-class precision/recall/F1/support, labels, and a confusion matrix where
rows are actual labels and columns are predicted labels.

## Metric notes

Metrics are represented between 0 and 1. Precision, recall, and F1 are computed
one-vs-rest per class; macro averages weight all classes equally, while weighted
averages weight classes by their actual support. Zero-denominator class scores
are set to 0. These values describe the supplied predictions and do not alone
prove generalization or explain why a model made an error.

python -m dslab.classification_eval `
  --input data/day-10/baseline_predictions.csv `
  --output reports/day-10/baseline-evaluation.json

python -m dslab.classification_eval `
  --input data/day-10/candidate_predictions.csv `
  --output reports/day-10/candidate-evaluation.json

python -m dslab.evaluation_compare `
  --baseline reports/day-10/baseline-evaluation.json `
  --candidate reports/day-10/candidate-evaluation.json `
  --config configs/day-11-regression-thresholds.json `
  --output reports/day-11/evaluation-comparison.json

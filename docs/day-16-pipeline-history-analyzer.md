# Day 16: Pipeline Run History and Reliability Analyzer

This tool analyzes saved JSON reports from the Day 15 pipeline orchestrator.
It does not rerun commands; it summarizes recorded pipeline history.

## Features

- Overall and per-pipeline success rates
- Successful and failed run counts
- Average and maximum execution duration
- Aggregated step counts
- Failed and timed-out step frequency
- Chronological run history
- UTF-8 BOM-compatible input

## Run

From the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m dslab.pipeline_history --input-dir data/day-16 --output reports/day-16/history-analysis.json
```

## Output

The JSON report contains `runs_analyzed`, `pipelines_analyzed`,
`overall_success_rate_percent`, `pipeline_summaries`,
`step_failure_frequency`, and `run_history`.

The analyzer validates required fields and rejects malformed reports. A step
status other than `passed` is counted as a failure. Results describe only the
saved reports; missing history cannot be inferred.
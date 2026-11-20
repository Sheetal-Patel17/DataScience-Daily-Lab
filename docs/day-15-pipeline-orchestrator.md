# Day 15: Data Pipeline Orchestrator

The orchestrator runs configured command steps sequentially and writes a JSON
report. It is useful for combining existing data-science scripts into a single
repeatable workflow without duplicating their logic.

## Run the example

From the repository root:

```powershell
python -m dslab.pipeline_orchestrator --config configs/day-15-pipeline.json --output reports/day-15/pipeline-report.json
```

Each step specifies a unique `name`, a `command` string array, and an optional
positive `timeout_seconds` (default: 60). Commands are executed directly without
a shell. Use executable names or absolute paths that are available in the
environment running the pipeline.

By default, execution stops at the first failed step. Set
`continue_on_error` to `true` at the configuration root to run the remaining
steps and collect their results.

The report records each step's status, exit code, captured standard output and
error, duration, and error details when a timeout or launch error occurs. The
CLI exits with code 0 only when every configured step passes; otherwise it
returns code 1. Invalid configurations are rejected before execution.

## Safety and limitations

Only run configurations you trust: each command can execute a program with the
permissions of the current user. The tool does not invoke a shell, but it is
not a sandbox. It currently runs steps sequentially and does not support
dependencies, retries, parallel execution, or secret management.

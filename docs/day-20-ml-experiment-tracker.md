

\# Day 20: ML Experiment Tracking and Reproducibility Manager



\## Overview



A lightweight Python utility for tracking machine-learning experiments,

comparing model runs, and maintaining reproducibility metadata.



\## Features



\- Record experiment names, run IDs, parameters and metrics.

\- Store timestamps in UTC.

\- Track random seeds.

\- Generate SHA-256 dataset fingerprints.

\- Filter and rank experiment runs.

\- Select the best run using a chosen metric.

\- Export experiment history to JSON and CSV.

\- Persist records safely using atomic file replacement.

\- Validate experiment metadata and metric values.



\## Quick Start



```python

from dslab.experiment\_tracker import ExperimentTracker



tracker = ExperimentTracker("reports/day-20/experiments.json")



tracker.log\_run(

&#x20;   experiment\_name="customer-churn",

&#x20;   params={

&#x20;       "learning\_rate": 0.01,

&#x20;       "epochs": 20

&#x20;   },

&#x20;   metrics={

&#x20;       "accuracy": 0.94,

&#x20;       "precision": 0.91,

&#x20;       "f1": 0.92

&#x20;   },

&#x20;   seed=42,

&#x20;   tags={"model": "random-forest"}

)



best = tracker.best\_run("f1", maximize=True)

print(best)



tracker.export\_json("reports/day-20/history.json")

tracker.export\_csv("reports/day-20/history.csv")

```



\## Dataset Reproducibility



Provide `dataset\_path` when logging a run. The tracker calculates

a SHA-256 fingerprint of the dataset file.



```python

tracker.log\_run(

&#x20;   experiment\_name="customer-churn",

&#x20;   params={"epochs": 20},

&#x20;   metrics={"f1": 0.92},

&#x20;   seed=42,

&#x20;   dataset\_path="data/day-20/customers.csv"

)

```



\## Run Tests



```powershell

python -m pytest tests/test\_experiment\_tracker.py -v

```



\## Design Decisions



\- Pure Python implementation without external runtime dependencies.

\- JSON storage for portability and inspectability.

\- Atomic replacement to reduce the risk of partially written storage.

\- Missing metrics are excluded from metric-specific comparisons.

\- The tracker records seeds but does not configure random generators.

\- Dataset fingerprints identify file contents, not semantic dataset equivalence.



\## Limitations



This is a local, single-process experiment tracker. It does not provide

distributed tracking, concurrent-write locking, model artifact storage,

or automatic experiment execution.




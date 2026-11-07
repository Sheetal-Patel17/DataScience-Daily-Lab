# Day 18: Time-Series Data Quality Auditor

## Overview

The Time-Series Data Quality Auditor analyzes timestamped sensor data and
produces a structured JSON quality report.

## Features

- Validates ISO 8601 timestamps and normalizes timezone offsets to UTC.
- Detects missing and invalid timestamps.
- Identifies duplicate timestamps.
- Detects records that appear out of chronological order.
- Finds missing sampling intervals.
- Flags non-aligned sampling intervals.
- Detects numeric outliers using the interquartile range (IQR) method.
- Supports configurable timestamp columns and sampling frequencies.
- Reads UTF-8 and UTF-8 BOM CSV files.
- Produces machine-readable JSON reports.

## Project files

- `src/dslab/timeseries_audit.py`: Auditor implementation.
- `tests/test_timeseries_audit.py`: Automated tests.
- `configs/day-18-timeseries-audit.json`: Example configuration.
- `data/day-18/sensor_readings.csv`: Example sensor dataset.

## Run the auditor

From the repository root:

```powershell
python -m dslab.timeseries_audit --input data/day-18/sensor_readings.csv --output reports/day-18-audit.json --config configs/day-18-timeseries-audit.json
```

## Run tests

```powershell
python -m pytest tests/test_timeseries_audit.py -v
```

## Sampling frequency

Supported frequency formats:

- `30s`: 30 seconds
- `15m`: 15 minutes
- `1h`: 1 hour
- `1d`: 1 day

## Report sections

The JSON report contains:

- Analysis metadata.
- Quality summary counts.
- Timestamp findings.
- Numeric outlier findings.

## Limitations

IQR outlier detection is a statistical screening technique, not proof of a
faulty sensor. Domain-specific thresholds and time-series-aware anomaly
detection may be needed for production systems.

The tool is intended for data-quality auditing and educational use, not
safety-critical monitoring.

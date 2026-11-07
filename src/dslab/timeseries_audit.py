from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from itertools import pairwise
from pathlib import Path
from typing import Any

FREQUENCY_PATTERN = re.compile(r"^([1-9]\d*)(s|m|h|d)$")


def parse_frequency(value: str) -> timedelta:
    """Convert a frequency such as 15m or 1h into a timedelta."""
    if not isinstance(value, str):
        raise TypeError("frequency must be a string.")

    match = FREQUENCY_PATTERN.fullmatch(value.strip())
    if not match:
        raise ValueError(
            "frequency must use a positive integer followed by s, m, h, or d."
        )

    amount = int(match.group(1))
    unit = match.group(2)
    seconds = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }[unit]
    return timedelta(seconds=amount * seconds)


def _parse_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 timestamp and normalize it to UTC."""
    parsed = datetime.fromisoformat(value.strip())

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC)


def _quantile(values: list[float], proportion: float) -> float:
    """Calculate a linearly interpolated quantile."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * proportion
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    fraction = position - lower
    return ordered[lower] + (
        ordered[upper] - ordered[lower]
    ) * fraction


def _numeric_column_audit(
    rows: list[dict[str, str]],
    columns: list[str],
) -> list[dict[str, Any]]:
    """Find IQR outliers in columns containing only numeric nonblank values."""
    findings = []

    for column in columns:
        values: list[tuple[int, float]] = []
        has_non_numeric = False

        for row_number, row in enumerate(rows, start=2):
            raw_value = (row.get(column) or "").strip()

            if not raw_value:
                continue

            try:
                number = float(raw_value)
            except ValueError:
                has_non_numeric = True
                break

            if not math.isfinite(number):
                has_non_numeric = True
                break

            values.append((row_number, number))

        if has_non_numeric or len(values) < 4:
            continue

        numeric_values = [value for _, value in values]
        q1 = _quantile(numeric_values, 0.25)
        q3 = _quantile(numeric_values, 0.75)
        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = [
            {"row": row_number, "value": value}
            for row_number, value in values
            if value < lower_bound or value > upper_bound
        ]

        findings.append({
            "column": column,
            "numeric_values_checked": len(values),
            "q1": round(q1, 6),
            "q3": round(q3, 6),
            "iqr": round(iqr, 6),
            "lower_bound": round(lower_bound, 6),
            "upper_bound": round(upper_bound, 6),
            "outlier_count": len(outliers),
            "outliers": outliers,
        })

    return findings


def audit_rows(
    rows: list[dict[str, str]],
    timestamp_column: str = "timestamp",
    frequency: str = "1h",
) -> dict[str, Any]:
    """Audit timestamp quality, expected intervals, and numeric outliers."""
    if not isinstance(rows, list) or not rows:
        raise ValueError("CSV must contain at least one data row.")

    if not isinstance(timestamp_column, str) or not timestamp_column.strip():
        raise ValueError("timestamp_column must be a non-empty string.")

    expected_interval = parse_frequency(frequency)

    if not all(isinstance(row, dict) for row in rows):
        raise TypeError("Every CSV row must be a dictionary.")

    columns = list(rows[0].keys())

    if timestamp_column not in columns:
        raise ValueError(
            f"Timestamp column '{timestamp_column}' was not found in the CSV."
        )

    valid_timestamps: list[tuple[int, datetime]] = []
    missing_timestamps = []
    invalid_timestamps = []

    for row_number, row in enumerate(rows, start=2):
        raw_value = row.get(timestamp_column)

        if raw_value is None or not raw_value.strip():
            missing_timestamps.append(row_number)
            continue

        try:
            timestamp = _parse_timestamp(raw_value)
        except (ValueError, TypeError):
            invalid_timestamps.append({
                "row": row_number,
                "value": raw_value,
            })
            continue

        valid_timestamps.append((row_number, timestamp))

    seen: dict[datetime, list[int]] = defaultdict(list)

    for row_number, timestamp in valid_timestamps:
        seen[timestamp].append(row_number)

    duplicates = [
        {
            "timestamp": timestamp.isoformat(),
            "rows": row_numbers,
        }
        for timestamp, row_numbers in sorted(seen.items())
        if len(row_numbers) > 1
    ]

    out_of_order = []
    previous_timestamp = None

    for row_number, timestamp in valid_timestamps:
        if (
            previous_timestamp is not None
            and timestamp < previous_timestamp[1]
        ):
            out_of_order.append({
                "row": row_number,
                "timestamp": timestamp.isoformat(),
                "previous_row": previous_timestamp[0],
                "previous_timestamp": previous_timestamp[1].isoformat(),
            })

        previous_timestamp = (row_number, timestamp)

    unique_timestamps = sorted(seen)
    missing_intervals = []

    for earlier, later in pairwise(unique_timestamps):
        difference = later - earlier

        if difference <= expected_interval:
            continue

        ratio = difference.total_seconds() / expected_interval.total_seconds()
        whole_steps = round(ratio)
        is_aligned = math.isclose(ratio, whole_steps, abs_tol=1e-9)

        missing_count = max(0, math.floor(ratio) - 1)

        missing_intervals.append({
            "from": earlier.isoformat(),
            "to": later.isoformat(),
            "missing_intervals": missing_count,
            "interval_aligned": is_aligned,
        })

    numeric_columns = [
        column for column in columns if column != timestamp_column
    ]
    outlier_findings = _numeric_column_audit(rows, numeric_columns)

    return {
        "schema_version": 1,
        "report_type": "timeseries-data-quality-audit",
        "analysis_metadata": {
            "generated_at_utc": datetime.now(UTC).isoformat(),
            "rows_analyzed": len(rows),
            "timestamp_column": timestamp_column,
            "expected_frequency": frequency,
        },
        "summary": {
            "valid_timestamps": len(valid_timestamps),
            "missing_timestamps": len(missing_timestamps),
            "invalid_timestamps": len(invalid_timestamps),
            "duplicate_timestamp_groups": len(duplicates),
            "out_of_order_records": len(out_of_order),
            "missing_intervals": sum(
                item["missing_intervals"] for item in missing_intervals
            ),
            "numeric_columns_analyzed": len(outlier_findings),
            "numeric_outliers": sum(
                item["outlier_count"] for item in outlier_findings
            ),
        },
        "timestamp_findings": {
            "missing_rows": missing_timestamps,
            "invalid_values": invalid_timestamps,
            "duplicates": duplicates,
            "out_of_order": out_of_order,
            "missing_intervals": missing_intervals,
        },
        "numeric_outlier_findings": outlier_findings,
    }


def load_csv(input_path: Path) -> list[dict[str, str]]:
    """Load CSV records using UTF-8 or UTF-8 with BOM."""
    if not input_path.exists() or not input_path.is_file():
        raise ValueError(f"Input CSV does not exist: {input_path}")

    try:
        with input_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(handle)

            if not reader.fieldnames:
                raise ValueError("CSV must contain a header row.")

            if len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ValueError("CSV contains duplicate column names.")

            if any(not name or not name.strip() for name in reader.fieldnames):
                raise ValueError("CSV contains an empty column name.")

            rows = list(reader)

    except (OSError, csv.Error) as exc:
        raise ValueError(f"Cannot read CSV file: {exc}") from exc

    if not rows:
        raise ValueError("CSV must contain at least one data row.")

    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timestamp-column", default="timestamp")
    parser.add_argument("--frequency", default="1h")
    parser.add_argument("--config", type=Path)

    args = parser.parse_args(argv)

    try:
        config: dict[str, Any] = {}

        if args.config:
            config = json.loads(args.config.read_text(encoding="utf-8-sig"))

            if not isinstance(config, dict):
                raise ValueError("Configuration must be a JSON object.")

            allowed_keys = {"timestamp_column", "frequency"}
            unknown_keys = set(config) - allowed_keys

            if unknown_keys:
                raise ValueError(
                    f"Unknown configuration settings: {sorted(unknown_keys)}"
                )

        timestamp_column = config.get(
            "timestamp_column",
            args.timestamp_column,
        )
        frequency = config.get("frequency", args.frequency)

        rows = load_csv(args.input)
        report = audit_rows(
            rows,
            timestamp_column=timestamp_column,
            frequency=frequency,
        )

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    except (ValueError, TypeError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    summary = report["summary"]

    print(f"Audited {report['analysis_metadata']['rows_analyzed']} rows.")
    print(f"Missing timestamps: {summary['missing_timestamps']}")
    print(f"Invalid timestamps: {summary['invalid_timestamps']}")
    print(f"Duplicate timestamp groups: {summary['duplicate_timestamp_groups']}")
    print(f"Out-of-order records: {summary['out_of_order_records']}")
    print(f"Missing intervals: {summary['missing_intervals']}")
    print(f"Numeric outliers: {summary['numeric_outliers']}")
    print(f"Report: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

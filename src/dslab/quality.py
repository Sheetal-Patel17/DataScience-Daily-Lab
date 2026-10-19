"""CSV profiling and data-quality checks."""

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def infer_type(values: list[str]) -> str:
    """Infer a simple type from non-empty string values."""
    if not values:
        return "empty"

    try:
        for value in values:
            int(value)
        return "integer"
    except ValueError:
        pass

    try:
        for value in values:
            float(value)
        return "number"
    except ValueError:
        return "string"


def profile_csv(path: str | Path) -> dict[str, Any]:
    """Profile a CSV and return a JSON-serializable quality report."""
    file_path = Path(path)

    if not file_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)

        if not reader.fieldnames:
            raise ValueError("CSV must contain a header row.")

        columns = reader.fieldnames

        if any(not column.strip() for column in columns):
            raise ValueError("CSV column names cannot be empty.")

        if len(set(columns)) != len(columns):
            raise ValueError("CSV column names must be unique.")

        rows = list(reader)

    for row_number, row in enumerate(rows, start=2):
        if None in row:
            raise ValueError(
                f"Row {row_number} has more values than the header."
            )
        if any(value is None for value in row.values()):
            raise ValueError(
                f"Row {row_number} has fewer values than the header."
            )

    missing_by_column = {
        column: sum(
            1 for row in rows if row[column].strip() == ""
        )
        for column in columns
    }

    column_types = {
        column: infer_type(
            [
                row[column].strip()
                for row in rows
                if row[column].strip()
            ]
        )
        for column in columns
    }

    row_signatures = [
        tuple(row[column] for column in columns)
        for row in rows
    ]
    signature_counts = Counter(row_signatures)
    duplicate_rows = sum(
        count - 1
        for count in signature_counts.values()
        if count > 1
    )

    total_cells = len(rows) * len(columns)
    missing_cells = sum(missing_by_column.values())

    return {
        "file_name": file_path.name,
        "row_count": len(rows),
        "column_count": len(columns),
        "columns": columns,
        "column_types": column_types,
        "missing_by_column": missing_by_column,
        "missing_cell_count": missing_cells,
        "missing_cell_rate": (
            missing_cells / total_cells if total_cells else 0.0
        ),
        "duplicate_row_count": duplicate_rows,
        "quality_status": (
            "needs_review"
            if missing_cells or duplicate_rows
            else "passed"
        ),
    }


def write_report(
    report: dict[str, Any],
    output_path: str | Path,
) -> None:
    """Write a quality report as formatted JSON."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

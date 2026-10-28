import csv
from pathlib import Path


def inspect_csv(path: str | Path) -> dict:
    """Inspect basic CSV structure without changing the source data."""
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {source}")
        columns = reader.fieldnames
        if any(not column.strip() for column in columns):
            raise ValueError(f"CSV has a blank column name: {source}")
        if len(columns) != len(set(columns)):
            raise ValueError(f"CSV has duplicate column names: {source}")

        row_count = 0
        missing_cells = 0
        for row in reader:
            if None in row:
                raise ValueError(f"CSV row has more values than the header: {source}")
            row_count += 1
            missing_cells += sum(
                not (row.get(column) or "").strip() for column in columns
            )

    return {
        "row_count": row_count,
        "column_count": len(columns),
        "columns": columns,
        "missing_cells": missing_cells,
    }
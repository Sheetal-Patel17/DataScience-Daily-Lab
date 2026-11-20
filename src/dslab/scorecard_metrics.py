import csv
from pathlib import Path


def read_dataset(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {source}")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"CSV has duplicate column names: {source}")
        rows = list(reader)
    return reader.fieldnames, rows


def count_missing_cells(
    columns: list[str], rows: list[dict[str, str]]
) -> int:
    return sum(
        not (row.get(column) or "").strip()
        for row in rows
        for column in columns
    )


def count_duplicate_rows(rows: list[dict[str, str]]) -> int:
    seen = set()
    duplicates = 0
    for row in rows:
        key = tuple(sorted(row.items()))
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates


def count_invalid_rows(
    rows: list[dict[str, str]],
    required_columns: list[str],
    numeric_ranges: dict,
) -> int:
    invalid = 0
    for row in rows:
        bad = any(
            not (row.get(column) or "").strip()
            for column in required_columns
        )
        for column, limits in numeric_ranges.items():
            value = (row.get(column) or "").strip()
            if not value:
                continue
            try:
                number = float(value)
            except ValueError:
                bad = True
                continue
            if number < limits["min"] or number > limits["max"]:
                bad = True
        invalid += bool(bad)
    return invalid

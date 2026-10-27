import csv
from pathlib import Path


def read_csv_dataset(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
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
        rows = []
        for row in reader:
            if None in row:
                raise ValueError(f"CSV row has more values than the header: {source}")
            if not any((value or "").strip() for value in row.values()):
                continue
            rows.append(
                {column: (row.get(column) or "").strip() for column in columns}
            )
    return columns, rows
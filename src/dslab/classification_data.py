import csv
from pathlib import Path


def read_label_pairs(
    path: str | Path,
    actual_column: str = "actual_label",
    predicted_column: str = "predicted_label",
) -> tuple[list[str], list[str]]:
    """Read actual/predicted labels from a CSV with validated headers."""
    if actual_column == predicted_column:
        raise ValueError("Actual and predicted columns must be different.")
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
        missing_columns = {actual_column, predicted_column} - set(columns)
        if missing_columns:
            names = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV is missing required column(s): {names}")

        actual_labels = []
        predicted_labels = []
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(
                    "CSV row has more values than the header "
                    f"at line {row_number}: {source}"
                )
            actual = (row.get(actual_column) or "").strip()
            predicted = (row.get(predicted_column) or "").strip()
            if not actual or not predicted:
                raise ValueError(
                    f"Blank label found at CSV line {row_number}: {source}"
                )
            actual_labels.append(actual)
            predicted_labels.append(predicted)

    if not actual_labels:
        raise ValueError(f"CSV contains no prediction rows: {source}")
    return actual_labels, predicted_labels

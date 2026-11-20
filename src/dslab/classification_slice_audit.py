import argparse
import csv
import json
from pathlib import Path

from dslab.classification_slices import classification_slice_metrics


def main():
    parser = argparse.ArgumentParser(
        description="Audit classification metrics across data groups."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--actual-column", default="actual_label")
    parser.add_argument("--predicted-column", default="predicted_label")
    parser.add_argument("--slice-column", default="region")
    parser.add_argument("--min-group-size", type=int, default=2)
    parser.add_argument(
        "--output",
        default="reports/day-12/classification-slices.json",
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    if not input_path.is_file():
        parser.error(f"Input CSV does not exist: {input_path}")

    with input_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            parser.error("CSV must contain a header row.")

        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            parser.error("CSV contains duplicate column names.")

        required = {
            args.actual_column,
            args.predicted_column,
            args.slice_column,
        }
        missing = required - set(reader.fieldnames)

        if missing:
            parser.error(f"Missing CSV columns: {sorted(missing)}")

        rows = list(reader)

    if not rows:
        parser.error("CSV contains no data rows.")

    for row_number, row in enumerate(rows, start=2):
        for column in required:
            value = row.get(column)
            if value is None or not value.strip():
                parser.error(
                    f"Blank value in column '{column}' at CSV row {row_number}."
                )

    result = classification_slice_metrics(
        actual=[row[args.actual_column] for row in rows],
        predicted=[row[args.predicted_column] for row in rows],
        groups=[row[args.slice_column] for row in rows],
        min_group_size=args.min_group_size,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Classification slice audit completed: {output_path}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

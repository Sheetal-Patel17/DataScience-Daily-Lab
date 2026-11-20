"""Command-line interface for CSV validation."""

import argparse
import csv
import sys
from pathlib import Path

from dslab.validation_engine import validate_rows
from dslab.validation_report import write_json_report
from dslab.validation_rules import load_rules


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate CSV data using configurable JSON rules."
    )
    parser.add_argument("--input", required=True, help="Path to input CSV.")
    parser.add_argument("--rules", required=True, help="Path to rules JSON.")
    parser.add_argument("--output", required=True, help="Path for JSON report.")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    with input_path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    rules = load_rules(args.rules)
    report = validate_rows(rows, rules, source=str(input_path))
    write_json_report(report, args.output)

    print(f"Source: {report.source}")
    print(f"Total rows: {report.total_rows}")
    print(f"Valid rows: {report.valid_rows}")
    print(f"Invalid rows: {report.invalid_rows}")
    print(f"Issues found: {len(report.issues)}")
    print(f"JSON report: {args.output}")

    return 0 if report.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())

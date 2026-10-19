"""Command-line interface for the data quality toolkit."""

import argparse
import json
import sys

from dslab.quality import profile_csv, write_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Profile a CSV file and report data-quality issues."
    )
    parser.add_argument("csv_file", help="Path to the input CSV file.")
    parser.add_argument(
        "--output",
        help="Optional path to save the JSON quality report.",
    )
    args = parser.parse_args()

    try:
        report = profile_csv(args.csv_file)
        print(json.dumps(report, indent=2, ensure_ascii=False))

        if args.output:
            write_report(report, args.output)
            print(f"\nReport saved to: {args.output}")

        return 0
    except (OSError, ValueError, csv_error()) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


def csv_error():
    """Return the CSV parser exception type."""
    import csv
    return csv.Error


if __name__ == "__main__":
    raise SystemExit(main())

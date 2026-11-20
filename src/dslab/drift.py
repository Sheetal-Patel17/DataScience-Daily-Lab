import argparse
import json
import sys
from pathlib import Path

from dslab.drift_detector import compare_csvs
from dslab.drift_report import write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare two CSV files and report schema drift."
    )
    parser.add_argument("--baseline", required=True, help="Path to baseline CSV")
    parser.add_argument("--current", required=True, help="Path to current CSV")
    parser.add_argument(
        "--output", default="reports/day-05/drift_report.json",
        help="Path for the JSON report",
    )
    parser.add_argument(
        "--config", help="Optional JSON config containing the missing-rate threshold"
    )
    parser.add_argument(
        "--threshold", type=float,
        help="Override the missing-rate increase threshold (0 to 1)",
    )
    args = parser.parse_args(argv)

    threshold = 0.2
    try:
        if args.config:
            config = json.loads(Path(args.config).read_text(encoding="utf-8"))
            threshold = float(config.get("missing_rate_increase_threshold", threshold))
        if args.threshold is not None:
            threshold = args.threshold

        report = compare_csvs(args.baseline, args.current, threshold)
        write_report(report, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"Compared {report.baseline_rows} baseline rows with "
          f"{report.current_rows} current rows.")
    print(f"Found {len(report.findings)} drift finding(s).")
    print(f"JSON report: {args.output}")
    return 1 if report.has_drift else 0


if __name__ == "__main__":
    raise SystemExit(main())

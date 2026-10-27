import argparse
import json
import sys
from pathlib import Path

from dslab.distribution_drift_report import write_drift_report
from dslab.drift_engine import compare_datasets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare CSV distributions and report possible data drift."
    )
    parser.add_argument("--baseline", required=True, help="Baseline CSV path")
    parser.add_argument("--current", required=True, help="Current CSV path")
    parser.add_argument(
        "--config",
        default="configs/day-07-distribution-drift.json",
        help="Threshold configuration JSON path",
    )
    parser.add_argument(
        "--output",
        default="reports/day-07/distribution-drift.json",
        help="Output JSON report path",
    )
    args = parser.parse_args(argv)
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8-sig"))
        report = compare_datasets(args.baseline, args.current, config)
        write_drift_report(report, args.output)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"Status: {report['status']}")
    print(f"Columns compared: {report['columns_compared']}")
    print(f"Columns with drift: {report['columns_with_drift']}")
    print(f"JSON report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
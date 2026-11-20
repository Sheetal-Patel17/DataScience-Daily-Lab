import argparse
import sys

from dslab.classification_report import write_evaluation_report
from dslab.evaluation_compare_engine import compare_evaluations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare classification evaluation reports for metric regressions."
    )
    parser.add_argument("--baseline", required=True, help="Baseline evaluation JSON")
    parser.add_argument("--candidate", required=True, help="Candidate evaluation JSON")
    parser.add_argument(
        "--config",
        default="configs/day-11-regression-thresholds.json",
        help="Allowed metric-drop thresholds JSON",
    )
    parser.add_argument(
        "--output",
        default="reports/day-11/evaluation-comparison.json",
        help="Output comparison JSON",
    )
    args = parser.parse_args(argv)

    try:
        report = compare_evaluations(args.baseline, args.candidate, args.config)
        write_evaluation_report(report, args.output)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"Status: {report['status']}")
    print(f"Regressed metrics: {len(report['regression_metrics'])}")
    print(f"JSON report: {args.output}")
    return 1 if report["regression_metrics"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

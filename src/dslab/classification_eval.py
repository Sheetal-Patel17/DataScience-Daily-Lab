import argparse
import sys
from pathlib import Path

from dslab.classification_data import read_label_pairs
from dslab.classification_metrics import classification_metrics
from dslab.classification_report import write_evaluation_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate classification predictions recorded in a CSV."
    )
    parser.add_argument(
        "--input", required=True, help="CSV with actual and predicted labels"
    )
    parser.add_argument(
        "--actual-column", default="actual_label", help="Ground-truth column"
    )
    parser.add_argument(
        "--predicted-column", default="predicted_label", help="Prediction column"
    )
    parser.add_argument(
        "--output",
        default="reports/day-10/evaluation.json",
        help="Output JSON report path",
    )
    args = parser.parse_args(argv)

    try:
        actual, predicted = read_label_pairs(
            args.input, args.actual_column, args.predicted_column
        )
        results = classification_metrics(actual, predicted)
        report = {
            "report_version": 1,
            "input_path": str(Path(args.input).resolve()),
            "actual_column": args.actual_column,
            "predicted_column": args.predicted_column,
            **results,
        }
        write_evaluation_report(report, args.output)
    except (OSError, ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"Rows evaluated: {report['row_count']}")
    print(f"Accuracy: {report['metrics']['accuracy']:.4f}")
    print(f"Macro F1: {report['metrics']['macro_f1']:.4f}")
    print(f"JSON report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

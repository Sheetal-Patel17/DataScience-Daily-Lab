import argparse
import json
import sys
from pathlib import Path

from dslab.scorecard_engine import build_scorecard
from dslab.scorecard_report import write_scorecard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a data quality scorecard for a CSV file."
    )
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument(
        "--config", default="configs/day-06-scorecard.json",
        help="Scoring rules JSON path",
    )
    parser.add_argument(
        "--output", default="reports/day-06/scorecard.json",
        help="Output scorecard JSON path",
    )
    args = parser.parse_args(argv)

    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        scorecard = build_scorecard(args.input, config)
        write_scorecard(scorecard, args.output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"Overall quality score: {scorecard.overall_score}/100")
    print(f"Grade: {scorecard.grade}")
    print(f"Rows: {scorecard.row_count}")
    print(f"Missing cells: {scorecard.missing_cells}")
    print(f"Duplicate rows: {scorecard.duplicate_rows}")
    print(f"Invalid rows: {scorecard.invalid_rows}")
    print(f"JSON report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

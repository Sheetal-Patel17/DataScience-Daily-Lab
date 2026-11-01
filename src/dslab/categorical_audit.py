"""Categorical feature auditing for CSV datasets."""

import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path


def normalize_category(value: str) -> str:
    """Normalize case and repeated whitespace for comparison."""
    return " ".join(value.strip().split()).casefold()


def read_table(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read a CSV file while preserving blank records for quality auditing."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        headers = next(reader, None)

        if not headers:
            raise ValueError("CSV must contain a header row.")
        if any(not name.strip() for name in headers):
            raise ValueError("CSV contains a blank column name.")
        if any(name != name.strip() for name in headers):
            raise ValueError("CSV column names must not have surrounding whitespace.")
        if len(headers) != len(set(headers)):
            raise ValueError("CSV contains duplicate column names.")

        rows = []
        for line_number, values in enumerate(reader, start=2):
            if not values:
                values = [""] * len(headers)
            if len(values) > len(headers):
                raise ValueError(f"Extra fields on CSV line {line_number}.")
            if len(values) < len(headers):
                raise ValueError(f"Missing fields on CSV line {line_number}.")
            rows.append(dict(zip(headers, values)))

    return headers, rows


def _validate_threshold(name: str, value: float) -> None:
    """Ensure a threshold is a finite fraction between zero and one."""
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be a finite number between 0 and 1.")


def audit_categorical_features(
    path: str | Path,
    rare_threshold: float = 0.05,
    high_cardinality_threshold: float = 0.50,
) -> dict:
    """Summarize categorical distributions and flag potential review areas."""
    _validate_threshold("rare_threshold", rare_threshold)
    _validate_threshold("high_cardinality_threshold", high_cardinality_threshold)

    headers, rows = read_table(path)
    total = len(rows)
    columns = {}

    for name in headers:
        values = [row[name].strip() for row in rows]
        nonblank = [value for value in values if value]
        counts = Counter(nonblank)

        variants = {}
        for value in nonblank:
            key = normalize_category(value)
            variants.setdefault(key, set()).add(value)

        normalized_variants = {
            key: sorted(items) for key, items in variants.items() if len(items) > 1
        }

        cardinality = len(counts)
        ratio = cardinality / len(nonblank) if nonblank else 0.0
        rare = {
            category: count
            for category, count in sorted(counts.items())
            if total and count / total < rare_threshold
        }

        flags = []
        if nonblank and ratio >= high_cardinality_threshold and cardinality > 1:
            flags.append("high_cardinality_review")
        if rare:
            flags.append("rare_categories_review")
        if normalized_variants:
            flags.append("normalization_variants_review")
        if len(nonblank) < total:
            flags.append("blank_values_review")

        columns[name] = {
            "row_count": total,
            "nonblank_count": len(nonblank),
            "blank_count": total - len(nonblank),
            "unique_count": cardinality,
            "cardinality_ratio": round(ratio, 4),
            "value_counts": dict(sorted(counts.items())),
            "rare_categories": rare,
            "normalization_variants": normalized_variants,
            "flags": flags,
        }

    flag_counts = Counter(
        flag for column in columns.values() for flag in column["flags"]
    )
    columns_needing_review = sum(bool(column["flags"]) for column in columns.values())

    return {
        "input_file": str(path),
        "summary": {
            "columns_audited": len(columns),
            "columns_needing_review": columns_needing_review,
            "columns_without_flags": len(columns) - columns_needing_review,
            "total_review_flags": sum(flag_counts.values()),
            "flag_counts": dict(sorted(flag_counts.items())),
        },
        "row_count": total,
        "column_count": len(headers),
        "rare_threshold": rare_threshold,
        "high_cardinality_threshold": high_cardinality_threshold,
        "columns": columns,
        "limitations": [
            "Flags are screening signals, not proof of data quality problems.",
            "Rare-category rates use the full row count as the denominator.",
            "This tool does not infer whether a column is categorical or an identifier.",
        ],
    }


def write_report(report: dict, output_path: str | Path) -> None:
    """Write an audit report as formatted JSON."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    """Run the categorical audit command-line interface."""
    parser = argparse.ArgumentParser(
        description="Audit categorical distributions in a CSV file."
    )
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument(
        "--output",
        default="reports/day-14/categorical-audit.json",
        help="Output JSON report path",
    )
    parser.add_argument("--rare-threshold", type=float, default=0.05)
    parser.add_argument("--high-cardinality-threshold", type=float, default=0.50)
    args = parser.parse_args(argv)

    try:
        report = audit_categorical_features(
            args.input, args.rare_threshold, args.high_cardinality_threshold
        )
        write_report(report, args.output)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"Rows: {report['row_count']}")
    print(f"Columns audited: {report['column_count']}")
    print(f"JSON report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

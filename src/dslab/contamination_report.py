"""Command-line interface for contamination audits."""
import argparse
import json
from pathlib import Path

from .contamination import audit_dataset


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Screen CSV datasets for duplicates and possible contamination."
    )
    parser.add_argument("--input", required=True, help="CSV file to audit")
    parser.add_argument("--compare", help="Optional second CSV file to compare")
    parser.add_argument("--output", required=True, help="Path for JSON report")
    args = parser.parse_args()

    try:
        result = audit_dataset(args.input, args.compare)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(f"Rows audited: {result.input_rows}")
    print(f"Duplicate rows: {result.duplicate_rows}")
    print(f"Cross-file matches: {result.cross_file_matches}")
    print(f"Findings: {len(result.findings)}")
    print(f"Report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

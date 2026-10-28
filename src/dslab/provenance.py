import argparse
import json
import sys

from dslab.provenance_engine import build_manifest
from dslab.provenance_report import write_json_report
from dslab.provenance_verify import verify_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create and verify dataset provenance manifests."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a manifest")
    create_parser.add_argument("--input", required=True, help="Input CSV path")
    create_parser.add_argument("--config", help="Optional JSON configuration path")
    create_parser.add_argument(
        "--output",
        default="reports/day-08/provenance-manifest.json",
        help="Manifest output JSON path",
    )

    verify_parser = subparsers.add_parser("verify", help="Verify a saved manifest")
    verify_parser.add_argument("--manifest", required=True, help="Manifest JSON path")
    verify_parser.add_argument(
        "--output", help="Optional path to save verification results as JSON"
    )

    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            manifest = build_manifest(args.input, args.config)
            write_json_report(manifest, args.output)
            print(f"Manifest created for: {manifest['dataset']['path']}")
            print(f"SHA-256: {manifest['dataset']['sha256']}")
            print(f"Rows: {manifest['dataset']['row_count']}")
            print(f"Columns: {manifest['dataset']['column_count']}")
            print(f"JSON manifest: {args.output}")
            return 0

        report = verify_manifest(args.manifest)
        if args.output:
            write_json_report(report, args.output)
        print(f"Verification status: {report['status']}")
        print(f"Checks passed: {report['checks_passed']}/{report['checks_total']}")
        if report["status"] != "verified":
            for check in report["checks"]:
                if not check["passed"]:
                    print(f"Mismatch: {check['name']}")
            return 1
        if args.output:
            print(f"Verification report: {args.output}")
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
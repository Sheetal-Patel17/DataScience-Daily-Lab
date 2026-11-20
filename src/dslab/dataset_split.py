import argparse
import json
import sys
from pathlib import Path

from dslab.split_data import read_csv_dataset
from dslab.split_engine import DEFAULT_RATIOS, split_dataset, validate_ratios
from dslab.split_report import build_split_report, write_split_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create reproducible train/validation/test CSV splits and audit leakage."
    )
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--config", default="configs/day-09-split.json", help="JSON split config")
    parser.add_argument("--output-dir", default="reports/day-09/splits", help="Directory for split CSVs and report")
    parser.add_argument("--seed", type=int, help="Override deterministic random seed")
    parser.add_argument("--train-ratio", type=float, help="Override train ratio")
    parser.add_argument("--validation-ratio", type=float, help="Override validation ratio")
    parser.add_argument("--test-ratio", type=float, help="Override test ratio")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--stratify-by", help="Preserve target label representation across splits")
    mode.add_argument("--group-column", help="Keep rows with the same entity value in one split")
    args = parser.parse_args(argv)

    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8-sig"))
        if not isinstance(config, dict):
            raise TypeError("Split configuration must be a JSON object.")
        configured_ratios = config.get("ratios", DEFAULT_RATIOS)
        if not isinstance(configured_ratios, dict):
            raise TypeError("Config field 'ratios' must be a JSON object.")
        ratios_source = {
            "train": args.train_ratio if args.train_ratio is not None else configured_ratios.get("train"),
            "validation": args.validation_ratio if args.validation_ratio is not None else configured_ratios.get("validation"),
            "test": args.test_ratio if args.test_ratio is not None else configured_ratios.get("test"),
        }
        ratios = validate_ratios(ratios_source)
        seed = args.seed if args.seed is not None else config.get("seed", 42)
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise TypeError("Config seed must be an integer.")

        columns, rows = read_csv_dataset(args.input)
        splits = split_dataset(
            rows, columns, ratios, seed=seed,
            stratify_by=args.stratify_by, group_column=args.group_column,
        )
        report = build_split_report(
            splits, columns, ratios, seed,
            stratify_by=args.stratify_by, group_column=args.group_column,
        )
        report_path = write_split_outputs(splits, columns, report, args.output_dir)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"Split status: {report['status']}")
    print(f"Mode: {report['mode']}")
    for name, count in report["split_counts"].items():
        print(f"{name.title()} rows: {count} ({report['actual_ratios'][name]:.1%})")
    print(f"Exact duplicate signatures shared across splits: {report['leakage_checks']['exact_duplicate_signatures_shared_across_splits']}")
    if report["warnings"]:
        for warning in report["warnings"]:
            print(f"Warning: {warning}")
    print(f"Split report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
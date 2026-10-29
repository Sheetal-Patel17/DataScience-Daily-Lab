import csv
import json
from pathlib import Path

from dslab.split_engine import SPLIT_NAMES


def build_split_report(
    splits: dict[str, list[dict[str, str]]],
    columns: list[str],
    ratios: dict[str, float],
    seed: int,
    stratify_by: str | None = None,
    group_column: str | None = None,
) -> dict:
    total_rows = sum(len(splits[name]) for name in SPLIT_NAMES)
    counts = {name: len(splits[name]) for name in SPLIT_NAMES}
    actual_ratios = {
        name: (counts[name] / total_rows if total_rows else 0.0)
        for name in SPLIT_NAMES
    }

    signatures_by_split = []
    for name in SPLIT_NAMES:
        signatures_by_split.append({tuple(row.get(column, "") for column in columns) for row in splits[name]})
    shared_signatures = set()
    for left in range(len(signatures_by_split)):
        for right in range(left + 1, len(signatures_by_split)):
            shared_signatures.update(signatures_by_split[left] & signatures_by_split[right])

    group_overlap_count = 0
    if group_column:
        group_sets = [
            {row[group_column] for row in splits[name] if row.get(group_column, "")}
            for name in SPLIT_NAMES
        ]
        seen = set()
        overlaps = set()
        for group_set in group_sets:
            overlaps.update(seen & group_set)
            seen.update(group_set)
        group_overlap_count = len(overlaps)

    target_distribution = None
    if stratify_by:
        all_labels = sorted({row[stratify_by] for split in splits.values() for row in split})
        target_distribution = {
            label: {name: sum(row[stratify_by] == label for row in splits[name]) for name in SPLIT_NAMES}
            for label in all_labels
        }

    warnings = []
    if shared_signatures:
        warnings.append(f"{len(shared_signatures)} exact row signature(s) occur in multiple splits.")
    if group_overlap_count:
        warnings.append(f"{group_overlap_count} group value(s) occur in multiple splits.")

    return {
        "report_version": 1,
        "status": "warnings" if warnings else "clean",
        "seed": seed,
        "mode": "group" if group_column else "stratified" if stratify_by else "random",
        "stratify_column": stratify_by,
        "group_column": group_column,
        "columns": columns,
        "total_rows": total_rows,
        "requested_ratios": ratios,
        "actual_ratios": actual_ratios,
        "split_counts": counts,
        "target_distribution": target_distribution,
        "leakage_checks": {
            "exact_duplicate_signatures_shared_across_splits": len(shared_signatures),
            "group_values_shared_across_splits": group_overlap_count,
        },
        "warnings": warnings,
        "limitations": [
            "A random split is not a substitute for time-aware splitting on temporal data.",
            "Stratification requires at least three rows for each target value.",
            "Group-aware splits may differ from requested row ratios because groups stay intact.",
            "Exact-row overlap checks do not detect every possible form of target leakage.",
        ],
    }


def write_split_outputs(
    splits: dict[str, list[dict[str, str]]],
    columns: list[str],
    report: dict,
    output_dir: str | Path,
) -> Path:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    for name in SPLIT_NAMES:
        output_path = destination / f"{name}.csv"
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="raise")
            writer.writeheader()
            writer.writerows(splits[name])
    report_path = destination / "split-report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path
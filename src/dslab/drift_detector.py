import csv
from pathlib import Path

from dslab.drift_models import DriftFinding, DriftReport
from dslab.drift_types import infer_column_type


def read_csv(path: str | Path) -> tuple[list[str], list[dict[str, str]]]:
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {source}")
        headers = reader.fieldnames
        if len(headers) != len(set(headers)):
            raise ValueError(f"CSV contains duplicate column names: {source}")
        rows = list(reader)
    return headers, rows


def compare_csvs(
    baseline_path: str | Path,
    current_path: str | Path,
    missing_rate_threshold: float = 0.2,
) -> DriftReport:
    if not 0 < missing_rate_threshold <= 1:
        raise ValueError("missing_rate_threshold must be greater than 0 and at most 1")

    old_headers, old_rows = read_csv(baseline_path)
    new_headers, new_rows = read_csv(current_path)
    findings = []

    for column in sorted(set(new_headers) - set(old_headers)):
        findings.append(DriftFinding(
            "added_column", column, "medium", "absent", "present",
            f"Column '{column}' was added.",
        ))

    for column in sorted(set(old_headers) - set(new_headers)):
        findings.append(DriftFinding(
            "removed_column", column, "high", "present", "absent",
            f"Column '{column}' was removed.",
        ))

    for column in sorted(set(old_headers) & set(new_headers)):
        old_type = infer_column_type([row.get(column, "") or "" for row in old_rows])
        new_type = infer_column_type([row.get(column, "") or "" for row in new_rows])
        if old_type != new_type and old_type != "unknown" and new_type != "unknown":
            findings.append(DriftFinding(
                "type_changed", column, "high", old_type, new_type,
                f"Column '{column}' changed type from {old_type} to {new_type}.",
            ))

    return DriftReport(
        str(baseline_path), str(current_path),
        len(old_rows), len(new_rows), findings,
    )

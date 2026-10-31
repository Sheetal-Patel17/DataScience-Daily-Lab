"""Dataset contamination and duplicate screening."""
from pathlib import Path

from .contamination_checks import (
    blank_value_counts,
    cross_file_findings,
    duplicate_findings,
    suspicious_column_findings,
    suspicious_columns,
)
from .contamination_models import AuditResult, Finding
from .contamination_normalize import read_csv


def audit_dataset(
    input_path: str | Path,
    compare_path: str | Path | None = None,
) -> AuditResult:
    headers, rows = read_csv(input_path)
    duplicate_rows, findings = duplicate_findings(rows, headers)
    flagged_columns = suspicious_columns(headers)
    findings.extend(suspicious_column_findings(flagged_columns))

    overlap = 0
    if compare_path is not None:
        other_headers, other_rows = read_csv(compare_path)
        shared = [column for column in headers if column in other_headers]
        if not shared:
            findings.append(Finding(
                "no_shared_columns", "info",
                "The files have no shared columns to compare.", 0,
            ))
        else:
            overlap, cross_findings = cross_file_findings(rows, other_rows, shared)
            findings.extend(cross_findings)

    blanks = blank_value_counts(rows, headers)
    columns_with_blanks = {
        column: count for column, count in blanks.items() if count
    }
    if columns_with_blanks:
        findings.append(Finding(
            "blank_values", "info",
            "Blank values were found; review whether they are expected.",
            sum(columns_with_blanks.values()),
            tuple(f"{name}:{count}" for name, count in list(columns_with_blanks.items())[:5]),
        ))

    return AuditResult(
        input_rows=len(rows),
        unique_rows=len(rows) - duplicate_rows,
        duplicate_rows=duplicate_rows,
        cross_file_matches=overlap,
        suspicious_columns=flagged_columns,
        findings=tuple(findings),
    )

"""Individual contamination screening checks."""
from collections import Counter
from .contamination_models import Finding
from .contamination_normalize import normalize_value, row_fingerprint


SUSPICIOUS_NAME_PARTS = (
    "target", "label", "outcome", "ground_truth", "ground truth",
    "prediction", "predicted", "future", "post_event", "post-event",
)


def duplicate_findings(rows: list[dict[str, str]], columns: list[str]) -> tuple[int, list[Finding]]:
    counts = Counter(row_fingerprint(row, columns) for row in rows)
    repeated = {key: count for key, count in counts.items() if count > 1}
    duplicate_rows = sum(count - 1 for count in repeated.values())
    examples = tuple(key[:12] for key in list(repeated)[:5])
    findings = []
    if duplicate_rows:
        findings.append(Finding(
            "duplicate_rows", "warning",
            "Exact duplicate rows were found after whitespace/case normalization.",
            duplicate_rows, examples,
        ))
    return duplicate_rows, findings


def cross_file_findings(
    left: list[dict[str, str]], right: list[dict[str, str]],
    columns: list[str],
) -> tuple[int, list[Finding]]:
    left_keys = {row_fingerprint(row, columns) for row in left}
    right_keys = {row_fingerprint(row, columns) for row in right}
    overlap = left_keys & right_keys
    findings = []
    if overlap:
        findings.append(Finding(
            "cross_file_overlap", "high",
            "Records overlap between the two files on shared columns.",
            len(overlap), tuple(sorted(key[:12] for key in overlap)[:5]),
        ))
    return len(overlap), findings


def suspicious_columns(headers: list[str]) -> tuple[str, ...]:
    return tuple(
        name for name in headers
        if any(part in name.casefold() for part in SUSPICIOUS_NAME_PARTS)
    )


def suspicious_column_findings(columns: tuple[str, ...]) -> list[Finding]:
    if not columns:
        return []
    return [Finding(
        "suspicious_column_name", "review",
        "Review these column names for target leakage; names alone do not prove leakage.",
        len(columns), columns[:5],
    )]


def normalized_duplicate_groups(
    rows: list[dict[str, str]], columns: list[str]
) -> list[tuple[str, ...]]:
    """Return row-number groups whose normalized values are identical."""
    groups: dict[str, list[int]] = {}
    for index, row in enumerate(rows, start=2):
        key = row_fingerprint(row, columns)
        groups.setdefault(key, []).append(index)
    return [
        tuple(str(number) for number in indexes)
        for indexes in groups.values() if len(indexes) > 1
    ]


def blank_value_counts(
    rows: list[dict[str, str]], columns: list[str]
) -> dict[str, int]:
    return {
        column: sum(not normalize_value(row.get(column, "")) for row in rows)
        for column in columns
    }

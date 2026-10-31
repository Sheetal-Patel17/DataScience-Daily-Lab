from dslab.contamination_checks import (
    blank_value_counts,
    duplicate_findings,
    normalized_duplicate_groups,
    suspicious_columns,
)


def test_duplicate_rows_are_detected():
    rows = [{"name": "Alice"}, {"name": " alice "}, {"name": "Bob"}]
    count, findings = duplicate_findings(rows, ["name"])
    assert count == 1
    assert findings[0].code == "duplicate_rows"


def test_suspicious_names_are_flagged_for_review():
    assert suspicious_columns(["age", "target_label"]) == ("target_label",)


def test_duplicate_groups_include_csv_line_numbers():
    rows = [{"id": "1"}, {"id": "1"}, {"id": "2"}]
    assert normalized_duplicate_groups(rows, ["id"]) == [("2", "3")]


def test_blank_counts_are_reported():
    rows = [{"name": "Alice"}, {"name": "  "}]
    assert blank_value_counts(rows, ["name"]) == {"name": 1}
from dslab.contamination_checks import duplicate_findings


def test_duplicate_detection_ignores_case_and_extra_spaces():
    rows = [
        {"name": "Alice Smith"},
        {"name": "  ALICE   SMITH  "},
        {"name": "Bob"},
    ]

    count, findings = duplicate_findings(rows, ["name"])

    assert count == 1
    assert len(findings) == 1
    assert findings[0].code == "duplicate_rows"

"""Tests for validation result data structures."""

from dslab.validation_models import ValidationIssue, ValidationReport


def test_issue_converts_to_dictionary():
    issue = ValidationIssue(2, "age", "range", "Too high.", "130")
    assert issue.to_dict()["field"] == "age"
    assert issue.to_dict()["row_number"] == 2


def test_report_counts_unique_invalid_rows():
    issues = [
        ValidationIssue(1, "name", "required", "Missing."),
        ValidationIssue(1, "age", "range", "Too high."),
        ValidationIssue(3, "city", "allowed_values", "Unknown."),
    ]
    report = ValidationReport("customers.csv", 4, issues)
    assert report.valid_rows == 2
    assert report.invalid_rows == 2
    assert report.is_valid is False


def test_empty_report_is_valid():
    report = ValidationReport("empty.csv", 0, [])
    assert report.is_valid
    assert report.to_dict()["summary"]["issue_count"] == 0

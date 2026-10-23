"""Tests for row-level validation rules."""

from dslab.validation_engine import validate_rows


def test_required_and_type_rules():
    report = validate_rows(
        [{"name": "", "age": "young"}],
        {"required": ["name"], "types": {"age": "integer"}},
    )
    assert {issue.rule for issue in report.issues} == {"required", "type"}


def test_numeric_range_rules():
    report = validate_rows(
        [{"age": "130"}, {"age": "-1"}],
        {"types": {"age": "integer"}, "ranges": {"age": {
            "min": 0, "max": 120
        }}},
    )
    assert len(report.issues) == 2
    assert all(issue.rule == "range" for issue in report.issues)


def test_allowed_values_and_string_length():
    report = validate_rows(
        [{"city": "Paris", "name": "X"}],
        {
            "allowed_values": {"city": ["Rajkot", "Surat"]},
            "string_lengths": {"name": {"min": 2, "max": 10}},
        },
    )
    assert {issue.rule for issue in report.issues} == {
        "allowed_values", "string_length"
    }


def test_unique_fields_report_later_duplicate():
    report = validate_rows(
        [{"id": "7"}, {"id": "7"}],
        {"unique": ["id"]},
    )
    assert len(report.issues) == 1
    assert report.issues[0].row_number == 2
    assert report.issues[0].rule == "unique"


def test_valid_rows_have_no_issues():
    report = validate_rows(
        [{"name": "Asha", "age": "22"}],
        {"required": ["name"], "types": {"age": "integer"}},
    )
    assert report.is_valid
    assert report.valid_rows == 1

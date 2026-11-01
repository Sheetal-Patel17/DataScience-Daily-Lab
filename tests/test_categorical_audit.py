import csv
import json

import pytest

from dslab.categorical_audit import (
    audit_categorical_features,
    main,
    normalize_category,
    read_table,
)


def test_normalize_category_collapses_spaces_and_case():
    assert normalize_category("  New   YORK ") == "new york"


def test_reports_basic_column_counts(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("city\nA\nB\nA\n", encoding="utf-8")
    report = audit_categorical_features(path)
    assert report["row_count"] == 3
    assert report["columns"]["city"]["unique_count"] == 2
    assert report["columns"]["city"]["value_counts"] == {"A": 2, "B": 1}


def test_blank_values_are_counted(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("city\nA\n\nB\n", encoding="utf-8")
    report = audit_categorical_features(path)
    assert report["columns"]["city"]["blank_count"] == 1
    assert "blank_values_review" in report["columns"]["city"]["flags"]


def test_normalized_variants_are_flagged(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("city\nAhmedabad\nahmedabad\n", encoding="utf-8")
    report = audit_categorical_features(path)
    assert "normalization_variants_review" in report["columns"]["city"]["flags"]


def test_high_cardinality_is_flagged(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("id\n1\n2\n3\n4\n", encoding="utf-8")
    report = audit_categorical_features(path, high_cardinality_threshold=0.5)
    assert "high_cardinality_review" in report["columns"]["id"]["flags"]


def test_rare_category_is_reported(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("kind\nA\nA\nA\nB\n", encoding="utf-8")
    report = audit_categorical_features(path, rare_threshold=0.30)
    assert report["columns"]["kind"]["rare_categories"] == {"B": 1}


@pytest.mark.parametrize("threshold", [-0.1, 1.1])
def test_rejects_invalid_rare_threshold(tmp_path, threshold):
    path = tmp_path / "data.csv"
    path.write_text("city\nA\n", encoding="utf-8")
    with pytest.raises(ValueError, match="rare_threshold"):
        audit_categorical_features(path, rare_threshold=threshold)


def test_rejects_empty_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="header"):
        read_table(path)


def test_rejects_duplicate_headers(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("city,city\nA,B\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        read_table(path)


def test_report_is_json_serializable(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("city\nA\nB\n", encoding="utf-8")
    report = audit_categorical_features(path)
    assert json.loads(json.dumps(report))["column_count"] == 1


def test_cli_writes_report(tmp_path):
    source = tmp_path / "input.csv"
    destination = tmp_path / "out" / "audit.json"
    source.write_text("city\nA\nB\n", encoding="utf-8")
    result = main(["--input", str(source), "--output", str(destination)])
    assert result == 0
    assert destination.exists()
    assert json.loads(destination.read_text(encoding="utf-8"))["row_count"] == 2


def test_cli_returns_error_for_missing_file(tmp_path):
    result = main(["--input", str(tmp_path / "missing.csv")])
    assert result == 2


@pytest.mark.parametrize("threshold", [float("nan"), float("inf"), float("-inf")])
def test_rejects_non_finite_rare_threshold(tmp_path, threshold):
    path = tmp_path / "data.csv"
    path.write_text("city\nAhmedabad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="finite number"):
        audit_categorical_features(path, rare_threshold=threshold)


@pytest.mark.parametrize("threshold", [float("nan"), float("inf"), float("-inf")])
def test_rejects_non_finite_cardinality_threshold(tmp_path, threshold):
    path = tmp_path / "data.csv"
    path.write_text("city\nAhmedabad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="finite number"):
        audit_categorical_features(path, high_cardinality_threshold=threshold)


def test_whitespace_only_values_are_counted_as_blank(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("city\nAhmedabad\n   \nSurat\n", encoding="utf-8")
    report = audit_categorical_features(path)
    assert report["columns"]["city"]["blank_count"] == 1
    assert report["columns"]["city"]["nonblank_count"] == 2


def test_header_only_csv_returns_zero_rows(tmp_path):
    path = tmp_path / "empty_data.csv"
    path.write_text("city,plan\n", encoding="utf-8")
    report = audit_categorical_features(path)
    assert report["row_count"] == 0
    assert report["columns"]["city"]["blank_count"] == 0
    assert report["columns"]["plan"]["unique_count"] == 0


def test_rejects_malformed_csv_extra_fields(tmp_path):
    path = tmp_path / "malformed.csv"
    path.write_text("city,plan\nAhmedabad,Basic,Unexpected\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Extra fields"):
        read_table(path)


def test_report_summary_counts_columns_and_flags(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("city,plan\nAhmedabad,Basic\nahmedabad,Premium\n", encoding="utf-8")

    report = audit_categorical_features(path)

    assert report["summary"]["columns_audited"] == 2
    assert report["summary"]["columns_needing_review"] == 2
    assert report["summary"]["columns_without_flags"] == 0
    assert report["summary"]["flag_counts"]["normalization_variants_review"] == 1
    assert report["summary"]["flag_counts"]["high_cardinality_review"] == 2


def test_report_summary_handles_empty_dataset(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("city,plan\n", encoding="utf-8")

    report = audit_categorical_features(path)

    assert report["summary"]["columns_audited"] == 2
    assert report["summary"]["columns_needing_review"] == 0
    assert report["summary"]["total_review_flags"] == 0
    assert report["summary"]["flag_counts"] == {}

def test_rejects_headers_with_surrounding_whitespace(tmp_path):
    path = tmp_path / "bad_headers.csv"
    path.write_text("city, city \nAhmedabad,Surat\n", encoding="utf-8")
    with pytest.raises(ValueError, match="surrounding whitespace"):
        read_table(path)


def test_rejects_unterminated_quoted_field(tmp_path):
    path = tmp_path / "bad_quotes.csv"
    path.write_text('"city,plan\nAhmedabad,Basic\n', encoding="utf-8")
    with pytest.raises(csv.Error):
        read_table(path)

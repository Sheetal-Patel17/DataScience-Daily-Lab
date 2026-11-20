"""Tests for the validation command-line interface."""

import json

from dslab.validation import main


def test_cli_writes_report_and_returns_failure_for_invalid_data(tmp_path):
    input_csv = tmp_path / "customers.csv"
    input_csv.write_text(
        "name,age\nAsha,22\n,130\n",
        encoding="utf-8",
    )
    rules_json = tmp_path / "rules.json"
    rules_json.write_text(
        json.dumps({
            "required": ["name"],
            "types": {"age": "integer"},
            "ranges": {"age": {"min": 0, "max": 120}},
        }),
        encoding="utf-8",
    )
    output_json = tmp_path / "report.json"

    result = main([
        "--input", str(input_csv),
        "--rules", str(rules_json),
        "--output", str(output_json),
    ])

    assert result == 1
    assert output_json.exists()
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    assert payload["summary"]["total_rows"] == 2
    assert payload["summary"]["invalid_rows"] == 1


def test_cli_returns_success_for_valid_data(tmp_path):
    input_csv = tmp_path / "customers.csv"
    input_csv.write_text("name\nAsha\n", encoding="utf-8")
    rules_json = tmp_path / "rules.json"
    rules_json.write_text(
        json.dumps({"required": ["name"]}),
        encoding="utf-8",
    )

    result = main([
        "--input", str(input_csv),
        "--rules", str(rules_json),
        "--output", str(tmp_path / "report.json"),
    ])
    assert result == 0

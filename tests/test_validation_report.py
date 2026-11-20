"""Tests for JSON validation report output."""

import json

from dslab.validation_engine import validate_rows
from dslab.validation_report import write_json_report


def test_report_is_written_as_json(tmp_path):
    report = validate_rows(
        [{"name": ""}],
        {"required": ["name"]},
        source="sample.csv",
    )
    destination = write_json_report(report, tmp_path / "reports" / "result.json")
    payload = json.loads(destination.read_text(encoding="utf-8"))

    assert payload["source"] == "sample.csv"
    assert payload["summary"]["invalid_rows"] == 1
    assert payload["issues"][0]["field"] == "name"

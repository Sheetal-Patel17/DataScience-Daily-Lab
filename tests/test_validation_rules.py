"""Tests for validation rule configuration."""

import json

import pytest

from dslab.validation_rules import load_rules


def test_load_valid_rules(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text(json.dumps({"required": ["name"]}), encoding="utf-8")
    assert load_rules(path)["required"] == ["name"]


def test_reject_unknown_rule_section(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text(json.dumps({"magic": True}), encoding="utf-8")
    with pytest.raises(ValueError, match="Unknown rule sections"):
        load_rules(path)


def test_reject_unsupported_type(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text(
        json.dumps({"types": {"age": "date"}}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="Unsupported type"):
        load_rules(path)


def test_reject_inverted_range(tmp_path):
    path = tmp_path / "rules.json"
    path.write_text(
        json.dumps({"ranges": {"age": {"min": 100, "max": 0}}}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Minimum exceeds maximum"):
        load_rules(path)

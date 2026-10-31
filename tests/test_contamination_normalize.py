import pytest

from dslab.contamination_normalize import normalize_value, read_csv, row_fingerprint


def test_normalization_ignores_case_and_extra_spaces():
    assert normalize_value("  New   YORK ") == "new york"


def test_fingerprint_uses_selected_columns():
    a = {"name": "Alice", "extra": "one"}
    b = {"name": " alice ", "extra": "two"}
    assert row_fingerprint(a, ["name"]) == row_fingerprint(b, ["name"])


def test_rejects_duplicate_headers(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("name,name\nA,B\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate column"):
        read_csv(path)


def test_rejects_rows_with_extra_fields(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("name\nAlice,Extra\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Extra fields"):
        read_csv(path)
def test_rejects_empty_csv_file(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        read_csv(path)

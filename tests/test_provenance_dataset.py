import pytest

from dslab.provenance_dataset import inspect_csv


def test_inspect_csv_counts_rows_columns_and_missing_cells(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text("id,name,amount\n1,Asha,10\n2,,20\n", encoding="utf-8")
    assert inspect_csv(path) == {
        "row_count": 2,
        "column_count": 3,
        "columns": ["id", "name", "amount"],
        "missing_cells": 1,
    }


def test_inspect_csv_rejects_duplicate_headers(tmp_path):
    path = tmp_path / "duplicate.csv"
    path.write_text("name,name\nAsha,Patel\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate column names"):
        inspect_csv(path)


def test_inspect_csv_rejects_extra_fields(tmp_path):
    path = tmp_path / "extra.csv"
    path.write_text("name\nAsha,extra\n", encoding="utf-8")
    with pytest.raises(ValueError, match="more values than the header"):
        inspect_csv(path)


def test_inspect_csv_rejects_missing_header(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="no header"):
        inspect_csv(path)
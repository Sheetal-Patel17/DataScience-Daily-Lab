import csv

import pytest

from dslab.drift_data import read_csv_dataset


def test_reads_csv_header_and_rows(tmp_path):
    path = tmp_path / "sample.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "age"])
        writer.writerow(["Asha", "25"])
    columns, rows = read_csv_dataset(path)
    assert columns == ["name", "age"]
    assert rows == [{"name": "Asha", "age": "25"}]


def test_rejects_duplicate_headers(tmp_path):
    path = tmp_path / "duplicate.csv"
    path.write_text("name,name\nAsha,Patel\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate column names"):
        read_csv_dataset(path)


def test_rejects_rows_with_extra_values(tmp_path):
    path = tmp_path / "extra.csv"
    path.write_text("name\nAsha,extra\n", encoding="utf-8")
    with pytest.raises(ValueError, match="more values"):
        read_csv_dataset(path)
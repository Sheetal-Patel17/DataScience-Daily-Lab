import csv

from dslab.scorecard_metrics import (
    count_duplicate_rows,
    count_invalid_rows,
    count_missing_cells,
    read_dataset,
)


def test_missing_cells_are_counted():
    rows = [{"name": "Asha", "city": ""}, {"name": "", "city": "Surat"}]
    assert count_missing_cells(["name", "city"], rows) == 2


def test_duplicate_rows_are_counted_after_first_occurrence():
    rows = [{"id": "1"}, {"id": "1"}, {"id": "2"}, {"id": "1"}]
    assert count_duplicate_rows(rows) == 2


def test_required_fields_and_numeric_ranges_flag_invalid_rows():
    rows = [
        {"name": "Asha", "age": "25"},
        {"name": "", "age": "30"},
        {"name": "Ravi", "age": "150"},
        {"name": "Meera", "age": "unknown"},
    ]
    assert count_invalid_rows(
        rows, ["name"], {"age": {"min": 0, "max": 120}}
    ) == 3


def test_reads_csv_header_and_rows(tmp_path):
    path = tmp_path / "sample.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "name"])
        writer.writerow([1, "Asha"])
    columns, rows = read_dataset(path)
    assert columns == ["id", "name"]
    assert rows == [{"id": "1", "name": "Asha"}]

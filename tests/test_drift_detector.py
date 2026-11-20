import csv

from dslab.drift_detector import compare_csvs


def make_csv(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def test_detects_added_and_removed_columns(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    make_csv(old, ["id", "email"], [[1, "a@example.com"]])
    make_csv(new, ["id", "city"], [[1, "Rajkot"]])

    report = compare_csvs(old, new)
    categories = {(item.category, item.column) for item in report.findings}
    assert ("added_column", "city") in categories
    assert ("removed_column", "email") in categories


def test_detects_changed_data_type(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    make_csv(old, ["age"], [[25], [30]])
    make_csv(new, ["age"], [["twenty-five"], ["thirty"]])

    report = compare_csvs(old, new)
    assert any(
        item.category == "type_changed" and item.column == "age"
        for item in report.findings
    )


def test_identical_csv_schema_has_no_drift(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    make_csv(old, ["id", "name"], [[1, "Asha"]])
    make_csv(new, ["id", "name"], [[2, "Ravi"]])

    assert compare_csvs(old, new).has_drift is False

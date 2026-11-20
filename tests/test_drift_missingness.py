import csv

from dslab.drift_detector import compare_csvs


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "age"])
        writer.writerows(rows)


def test_detects_increased_missing_rate(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    write_csv(old, [[1, 20], [2, 30], [3, 40], [4, 50]])
    write_csv(new, [[1, 20], [2, ""], [3, ""], [4, ""]])

    report = compare_csvs(old, new, missing_rate_threshold=0.2)
    assert any(
        item.category == "missing_rate_increased" and item.column == "age"
        for item in report.findings
    )


def test_missing_rate_below_threshold_is_not_reported(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    write_csv(old, [[1, 20], [2, 30], [3, 40], [4, 50]])
    write_csv(new, [[1, 20], [2, 30], [3, 40], [4, ""]])

    report = compare_csvs(old, new, missing_rate_threshold=0.3)
    assert not any(
        item.category == "missing_rate_increased" for item in report.findings
    )


def test_invalid_threshold_is_rejected(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    write_csv(old, [[1, 20]])
    write_csv(new, [[1, 20]])

    import pytest
    with pytest.raises(ValueError):
        compare_csvs(old, new, missing_rate_threshold=0)

import csv

import pytest

from dslab.classification_data import read_label_pairs


def test_reads_actual_and_predicted_columns(tmp_path):
    path = tmp_path / "predictions.csv"
    path.write_text(
        "actual_label,predicted_label\ncat,cat\ndog,cat\n", encoding="utf-8"
    )
    assert read_label_pairs(path) == (["cat", "dog"], ["cat", "cat"])


def test_supports_custom_column_names(tmp_path):
    path = tmp_path / "custom.csv"
    path.write_text("truth,guess\nyes,no\n", encoding="utf-8")
    assert read_label_pairs(path, "truth", "guess") == (["yes"], ["no"])


def test_rejects_duplicate_headers(tmp_path):
    path = tmp_path / "duplicate.csv"
    path.write_text("actual_label,actual_label\ncat,cat\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate column names"):
        read_label_pairs(path)


def test_rejects_blank_labels(tmp_path):
    path = tmp_path / "blank.csv"
    path.write_text("actual_label,predicted_label\ncat,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Blank label"):
        read_label_pairs(path)


def test_rejects_rows_with_extra_fields(tmp_path):
    path = tmp_path / "extra.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["actual_label", "predicted_label"])
        writer.writerow(["cat", "cat", "extra"])
    with pytest.raises(ValueError, match="more values than the header"):
        read_label_pairs(path)


def test_rejects_empty_dataset(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("actual_label,predicted_label\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no prediction rows"):
        read_label_pairs(path)


def test_rejects_same_actual_and_predicted_column(tmp_path):
    path = tmp_path / "same-column.csv"
    path.write_text("label\ncat\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be different"):
        read_label_pairs(path, "label", "label")

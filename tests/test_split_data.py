import pytest

from dslab.split_data import read_csv_dataset


def test_reads_header_and_rows(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text("id,name\n1,Asha\n2,Ravi\n", encoding="utf-8")
    columns, rows = read_csv_dataset(path)
    assert columns == ["id", "name"]
    assert rows[0] == {"id": "1", "name": "Asha"}
    assert len(rows) == 2


def test_rejects_duplicate_headers(tmp_path):
    path = tmp_path / "duplicate.csv"
    path.write_text("id,id\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate column names"):
        read_csv_dataset(path)


def test_rejects_extra_values(tmp_path):
    path = tmp_path / "extra.csv"
    path.write_text("id\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="more values"):
        read_csv_dataset(path)
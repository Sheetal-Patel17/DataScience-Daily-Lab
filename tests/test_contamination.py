import json

from dslab.contamination import audit_dataset


def test_audit_counts_duplicates_and_suspicious_columns(tmp_path):
    path = tmp_path / "train.csv"
    path.write_text(
        "id,name,target_label\n1,Alice,0\n2,Bob,1\n2, bob ,1\n",
        encoding="utf-8",
    )
    result = audit_dataset(path)
    assert result.input_rows == 3
    assert result.duplicate_rows == 1
    assert result.suspicious_columns == ("target_label",)


def test_cross_file_overlap_uses_shared_columns(tmp_path):
    first = tmp_path / "train.csv"
    second = tmp_path / "test.csv"
    first.write_text("id,name\n1,Alice\n2,Bob\n", encoding="utf-8")
    second.write_text("id,name,extra\n2,Bob,x\n3,Cara,y\n", encoding="utf-8")
    result = audit_dataset(first, second)
    assert result.cross_file_matches == 1
    assert any(item.code == "cross_file_overlap" for item in result.findings)


def test_json_report_is_serializable(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("id\n1\n", encoding="utf-8")
    result = audit_dataset(path)
    encoded = json.dumps(result.to_dict())
    assert '"input_rows": 1' in encoded


def test_no_shared_columns_does_not_crash(tmp_path):
    first = tmp_path / "a.csv"
    second = tmp_path / "b.csv"
    first.write_text("name\nAlice\n", encoding="utf-8")
    second.write_text("city\nLondon\n", encoding="utf-8")
    result = audit_dataset(first, second)
    assert any(item.code == "no_shared_columns" for item in result.findings)

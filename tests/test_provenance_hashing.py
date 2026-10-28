from dslab.provenance_hashing import sha256_file


def test_sha256_is_stable_for_same_file(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")
    assert sha256_file(path) == sha256_file(path)


def test_sha256_changes_when_file_changes(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("first", encoding="utf-8")
    first_hash = sha256_file(path)
    path.write_text("second", encoding="utf-8")
    assert sha256_file(path) != first_hash
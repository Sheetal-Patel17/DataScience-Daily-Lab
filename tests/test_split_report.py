from dslab.split_report import build_split_report, write_split_outputs


def test_report_detects_exact_rows_shared_between_splits(tmp_path):
    duplicate = {"id": "1", "target": "yes"}
    splits = {
        "train": [duplicate],
        "validation": [duplicate.copy()],
        "test": [{"id": "3", "target": "no"}],
    }
    report = build_split_report(splits, ["id", "target"], {"train": 0.5, "validation": 0.25, "test": 0.25}, 4)
    assert report["status"] == "warnings"
    assert report["leakage_checks"]["exact_duplicate_signatures_shared_across_splits"] == 1


def test_writer_creates_three_csv_files_and_report(tmp_path):
    splits = {
        "train": [{"id": "1"}],
        "validation": [{"id": "2"}],
        "test": [{"id": "3"}],
    }
    report = build_split_report(splits, ["id"], {"train": 1 / 3, "validation": 1 / 3, "test": 1 / 3}, 9)
    report_path = write_split_outputs(splits, ["id"], report, tmp_path / "nested")
    assert report_path.exists()
    assert (tmp_path / "nested" / "train.csv").read_text(encoding="utf-8").splitlines() == ["id", "1"]
    assert (tmp_path / "nested" / "validation.csv").exists()
    assert (tmp_path / "nested" / "test.csv").exists()
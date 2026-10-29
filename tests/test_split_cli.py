import csv
import json

from dslab.dataset_split import main


def create_dataset(path, count=24):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "customer", "target"])
        for index in range(count):
            writer.writerow([f"R{index:03d}", f"C{index // 4}", "yes" if index % 4 == 0 else "no"])


def test_cli_creates_splits_and_report(tmp_path):
    dataset = tmp_path / "data.csv"
    config = tmp_path / "split.json"
    create_dataset(dataset)
    config.write_text(json.dumps({"ratios": {"train": 0.7, "validation": 0.15, "test": 0.15}, "seed": 42}), encoding="utf-8")
    output = tmp_path / "output"
    code = main(["--input", str(dataset), "--config", str(config), "--output-dir", str(output), "--group-column", "customer"])
    assert code == 0
    report = json.loads((output / "split-report.json").read_text(encoding="utf-8"))
    assert report["mode"] == "group"
    assert report["leakage_checks"]["group_values_shared_across_splits"] == 0
    assert sum(report["split_counts"].values()) == 24


def test_cli_supports_target_stratification(tmp_path):
    dataset = tmp_path / "data.csv"
    create_dataset(dataset)
    output = tmp_path / "output"
    assert main(["--input", str(dataset), "--output-dir", str(output), "--stratify-by", "target"]) == 0
    report = json.loads((output / "split-report.json").read_text(encoding="utf-8"))
    assert report["mode"] == "stratified"
    assert report["target_distribution"]["yes"]["train"] > 0
    assert report["target_distribution"]["yes"]["test"] > 0


def test_cli_returns_error_for_missing_input(capsys, tmp_path):
    code = main(["--input", str(tmp_path / "missing.csv"), "--config", str(tmp_path / "missing.json")])
    assert code == 2
    assert "Error:" in capsys.readouterr().err
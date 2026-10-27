import csv
import json

from dslab.distribution_drift import main
from dslab.drift_engine import compare_datasets


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["age", "city", "note"])
        writer.writerows(rows)


def test_engine_flags_numeric_categorical_and_missing_drift(tmp_path):
    baseline = tmp_path / "baseline.csv"
    current = tmp_path / "current.csv"
    write_csv(baseline, [
        [20, "Surat", "x"], [21, "Surat", "x"],
        [22, "Rajkot", "x"], [23, "Rajkot", "x"],
    ])
    write_csv(current, [
        [40, "Ahmedabad", "x"], [41, "Ahmedabad", "x"],
        [42, "Ahmedabad", ""], [43, "Ahmedabad", ""],
    ])
    report = compare_datasets(str(baseline), str(current), {})
    assert report["status"] == "drift_detected"
    assert report["columns_compared"] == 3
    assert report["columns_with_drift"] >= 2
    assert report["added_columns"] == []
    assert report["removed_columns"] == []


def test_engine_lists_added_and_removed_columns(tmp_path):
    baseline = tmp_path / "baseline.csv"
    current = tmp_path / "current.csv"
    baseline.write_text("age,old_field\n20,x\n", encoding="utf-8")
    current.write_text("age,new_field\n21,y\n", encoding="utf-8")
    report = compare_datasets(str(baseline), str(current), {})
    assert report["added_columns"] == ["new_field"]
    assert report["removed_columns"] == ["old_field"]


def test_cli_writes_json_report(tmp_path):
    baseline = tmp_path / "baseline.csv"
    current = tmp_path / "current.csv"
    config = tmp_path / "config.json"
    output = tmp_path / "nested" / "report.json"
    write_csv(baseline, [[20, "Surat", "x"], [21, "Rajkot", "x"]])
    write_csv(current, [[40, "Ahmedabad", "x"], [41, "Ahmedabad", "x"]])
    config.write_text(json.dumps({}), encoding="utf-8")
    code = main([
        "--baseline", str(baseline),
        "--current", str(current),
        "--config", str(config),
        "--output", str(output),
    ])
    assert code == 0
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "drift_detected"


def test_cli_returns_error_for_missing_input(capsys, tmp_path):
    config = tmp_path / "config.json"
    config.write_text("{}", encoding="utf-8")
    code = main([
        "--baseline", str(tmp_path / "missing.csv"),
        "--current", str(tmp_path / "current.csv"),
        "--config", str(config),
        "--output", str(tmp_path / "report.json"),
    ])
    assert code == 2
    assert "Error:" in capsys.readouterr().err
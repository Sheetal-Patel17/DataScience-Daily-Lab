import json

from dslab.evaluation_compare import main


def write_report(path, accuracy):
    metrics = {
        "accuracy": accuracy,
        "macro_precision": 0.9,
        "macro_recall": 0.9,
        "macro_f1": 0.9,
        "weighted_f1": 0.9,
    }
    path.write_text(json.dumps({"metrics": metrics}), encoding="utf-8")


def test_cli_writes_no_regression_report(tmp_path):
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    config = tmp_path / "config.json"
    output = tmp_path / "out" / "comparison.json"
    write_report(baseline, 0.9)
    write_report(candidate, 0.88)
    config.write_text(
        json.dumps({"metric_drop_thresholds": {"accuracy": 0.03}}), encoding="utf-8"
    )
    code = main([
        "--baseline", str(baseline), "--candidate", str(candidate),
        "--config", str(config), "--output", str(output),
    ])
    assert code == 0
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["status"] == "no_significant_regression"


def test_cli_returns_one_when_regression_exceeds_threshold(tmp_path):
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    config = tmp_path / "config.json"
    write_report(baseline, 0.95)
    write_report(candidate, 0.8)
    config.write_text(
        json.dumps({"metric_drop_thresholds": {"accuracy": 0.03}}), encoding="utf-8"
    )
    code = main([
        "--baseline", str(baseline),
        "--candidate", str(candidate),
        "--config", str(config),
    ])
    assert code == 1


def test_cli_returns_two_for_invalid_input(tmp_path, capsys):
    config = tmp_path / "config.json"
    config.write_text("{}", encoding="utf-8")
    code = main([
        "--baseline", str(tmp_path / "missing1.json"),
        "--candidate", str(tmp_path / "missing2.json"),
        "--config", str(config),
    ])
    assert code == 2
    assert "Error:" in capsys.readouterr().err

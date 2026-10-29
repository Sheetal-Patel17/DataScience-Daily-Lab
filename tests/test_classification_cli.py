import json

from dslab.classification_eval import main


def test_cli_writes_evaluation_report(tmp_path):
    source = tmp_path / "predictions.csv"
    source.write_text(
        "actual_label,predicted_label\ncat,cat\ndog,cat\n", encoding="utf-8"
    )
    output = tmp_path / "nested" / "report.json"
    assert main(["--input", str(source), "--output", str(output)]) == 0
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["row_count"] == 2
    assert saved["metrics"]["accuracy"] == 0.5
    assert saved["confusion_matrix"]["dog"]["cat"] == 1


def test_cli_returns_error_for_missing_file(capsys, tmp_path):
    assert main(["--input", str(tmp_path / "missing.csv")]) == 2
    assert "Error:" in capsys.readouterr().err

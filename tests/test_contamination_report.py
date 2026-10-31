import json
import subprocess
import sys


def test_cli_writes_json_report(tmp_path):
    source = tmp_path / "data.csv"
    report = tmp_path / "report.json"
    source.write_text("id\n1\n1\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "dslab.contamination_report",
         "--input", str(source), "--output", str(report)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["duplicate_rows"] == 1


def test_cli_requires_input():
    result = subprocess.run(
        [sys.executable, "-m", "dslab.contamination_report"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "dslab.drift", *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_writes_report_and_returns_one_when_drift_exists(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    output = tmp_path / "report.json"
    old.write_text("id,name\n1,Asha\n", encoding="utf-8")
    new.write_text("id,name,city\n1,Asha,Rajkot\n", encoding="utf-8")

    result = run_cli(
        "--baseline", old, "--current", new, "--output", output,
    )

    assert result.returncode == 1
    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8"))["has_drift"] is True


def test_cli_returns_zero_when_no_drift_exists(tmp_path):
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"
    output = tmp_path / "report.json"
    old.write_text("id,name\n1,Asha\n", encoding="utf-8")
    new.write_text("id,name\n2,Ravi\n", encoding="utf-8")

    result = run_cli(
        "--baseline", old, "--current", new, "--output", output,
    )

    assert result.returncode == 0
    assert json.loads(output.read_text(encoding="utf-8"))["has_drift"] is False


def test_cli_reports_invalid_input(tmp_path):
    result = run_cli(
        "--baseline", tmp_path / "missing.csv",
        "--current", tmp_path / "also-missing.csv",
        "--output", tmp_path / "report.json",
    )
    assert result.returncode == 2
    assert "Error:" in result.stderr

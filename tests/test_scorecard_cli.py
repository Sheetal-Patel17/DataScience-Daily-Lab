import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cli_creates_scorecard_report(tmp_path):
    output = tmp_path / "scorecard.json"
    result = subprocess.run(
        [
            sys.executable, "-m", "dslab.scorecard",
            "--input", "data/day-06/customers.csv",
            "--config", "configs/day-06-scorecard.json",
            "--output", str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert "overall_score" in saved
    assert "recommendations" in saved
    assert "Grade:" in result.stdout


def test_cli_returns_error_for_missing_input(tmp_path):
    result = subprocess.run(
        [
            sys.executable, "-m", "dslab.scorecard",
            "--input", str(tmp_path / "missing.csv"),
            "--output", str(tmp_path / "report.json"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Error:" in result.stderr

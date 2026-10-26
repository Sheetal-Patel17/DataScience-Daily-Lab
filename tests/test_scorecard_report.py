import json

from dslab.scorecard_models import QualityScorecard
from dslab.scorecard_report import write_scorecard


def test_report_writer_creates_parent_directory_and_json(tmp_path):
    card = QualityScorecard(
        "sample.csv", 2, 2, 0, 4, 0, 0,
        100, 100, 100, 100, "Excellent", ["No issues found."],
    )
    output = tmp_path / "nested" / "scorecard.json"
    write_scorecard(card, output)
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["grade"] == "Excellent"
    assert saved["overall_score"] == 100

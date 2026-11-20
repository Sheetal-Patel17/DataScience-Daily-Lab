import csv
import json
from pathlib import Path

import pytest

from dslab.scorecard_engine import build_scorecard, grade_score

ROOT = Path(__file__).resolve().parents[1]


def load_config():
    return json.loads(
        (ROOT / "configs/day-06-scorecard.json").read_text(encoding="utf-8")
    )


def write_csv(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def test_sample_dataset_produces_actionable_scorecard():
    card = build_scorecard(ROOT / "data/day-06/customers.csv", load_config())
    assert 0 <= card.overall_score <= 100
    assert card.row_count == 7
    assert card.duplicate_rows == 1
    assert card.invalid_rows >= 1
    assert card.recommendations


def test_clean_dataset_scores_one_hundred(tmp_path):
    path = tmp_path / "clean.csv"
    write_csv(path, ["id", "name", "age"], [[1, "Asha", 25], [2, "Ravi", 30]])
    config = load_config()
    config["required_columns"] = ["id", "name"]
    card = build_scorecard(path, config)
    assert card.overall_score == 100
    assert card.grade == "Excellent"


def test_grade_boundaries():
    grades = {
        "excellent": 90,
        "good": 75,
        "needs_improvement": 50,
    }
    assert grade_score(90, grades) == "Excellent"
    assert grade_score(80, grades) == "Good"
    assert grade_score(60, grades) == "Needs Improvement"
    assert grade_score(20, grades) == "Poor"


def test_negative_weights_are_rejected(tmp_path):
    path = tmp_path / "sample.csv"
    write_csv(path, ["id"], [[1]])
    config = load_config()
    config["weights"]["completeness"] = -1
    with pytest.raises(ValueError):
        build_scorecard(path, config)

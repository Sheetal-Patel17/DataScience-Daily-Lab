from dslab.scorecard_models import QualityScorecard


def test_scorecard_serializes_to_dictionary():
    card = QualityScorecard(
        "customers.csv", 5, 3, 1, 15, 0, 0,
        93.33, 100.0, 100.0, 97.33, "Excellent", [],
    )
    result = card.to_dict()
    assert result["file_name"] == "customers.csv"
    assert result["overall_score"] == 97.33
    assert result["recommendations"] == []

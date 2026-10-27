from dslab.drift_categorical import (
    category_proportions,
    compare_categorical,
    total_variation_distance,
)


def test_category_proportions_sum_to_one():
    proportions = category_proportions(["A", "A", "B"])
    assert proportions == {"A": 2 / 3, "B": 1 / 3}


def test_total_variation_is_zero_for_same_distribution():
    assert total_variation_distance(["A", "B"], ["A", "B"]) == 0.0


def test_total_variation_detects_shift():
    assert total_variation_distance(["A", "A", "B"], ["B", "B", "A"]) > 0


def test_categorical_comparison_has_expected_shape():
    result = compare_categorical(["A", "B"], ["B", "B"])
    assert result["kind"] == "categorical"
    assert result["total_variation_distance"] == 0.5
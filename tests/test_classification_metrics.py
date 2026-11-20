import pytest

from dslab.classification_metrics import classification_metrics


def test_calculates_accuracy_and_class_metrics():
    report = classification_metrics(
        ["cat", "dog", "cat", "dog"], ["cat", "cat", "cat", "dog"]
    )
    assert report["metrics"]["accuracy"] == 0.75
    assert report["per_class"]["cat"]["precision"] == 0.666667
    assert report["per_class"]["cat"]["recall"] == 1.0
    assert report["per_class"]["dog"]["support"] == 2


def test_confusion_matrix_rows_are_actual_and_columns_are_predicted():
    report = classification_metrics(["cat", "dog"], ["dog", "dog"])
    assert report["confusion_matrix"]["cat"]["dog"] == 1
    assert report["confusion_matrix"]["dog"]["dog"] == 1


def test_macro_and_weighted_metrics_are_bounded():
    report = classification_metrics(["a", "a", "a", "b"], ["a", "b", "a", "b"])
    for value in report["metrics"].values():
        assert 0 <= value <= 1


def test_zero_division_scores_are_zero():
    report = classification_metrics(["cat", "cat"], ["dog", "dog"])
    assert report["per_class"]["cat"]["precision"] == 0
    assert report["per_class"]["cat"]["recall"] == 0
    assert report["per_class"]["dog"]["support"] == 0


def test_rejects_empty_or_mismatched_inputs():
    with pytest.raises(ValueError, match="must not be empty"):
        classification_metrics([], [])
    with pytest.raises(ValueError, match="equal lengths"):
        classification_metrics(["cat"], ["cat", "dog"])


def test_rejects_empty_label_values():
    with pytest.raises(ValueError, match="non-empty"):
        classification_metrics([""], ["cat"])

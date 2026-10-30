import pytest

from dslab.classification_slices import classification_slice_metrics


def test_metrics_are_calculated_for_each_group():
    result = classification_slice_metrics(
        actual=["cat", "dog", "cat", "dog"],
        predicted=["cat", "dog", "dog", "dog"],
        groups=["north", "north", "south", "south"],
    )

    assert result["row_count"] == 4
    assert result["slice_count"] == 2
    assert result["evaluated_slice_count"] == 2
    assert result["slices"]["north"]["metrics"]["accuracy"] == 1.0
    assert result["slices"]["south"]["metrics"]["accuracy"] == 0.5


def test_small_group_is_marked_insufficient():
    result = classification_slice_metrics(
        actual=["cat", "dog", "cat"],
        predicted=["cat", "dog", "cat"],
        groups=["north", "north", "west"],
        min_group_size=2,
    )

    assert result["slices"]["west"]["status"] == "insufficient_data"
    assert result["slices"]["west"]["metrics"] is None
    assert result["evaluated_slice_count"] == 1


def test_accuracy_gap_warning_is_generated():
    result = classification_slice_metrics(
        actual=["cat", "dog", "cat", "dog"],
        predicted=["cat", "dog", "dog", "cat"],
        groups=["north", "north", "south", "south"],
    )

    assert result["accuracy_gap"] == 1.0
    assert any("at least 0.15" in warning for warning in result["warnings"])


def test_groups_are_sorted():
    result = classification_slice_metrics(
        actual=["cat", "dog", "cat", "dog"],
        predicted=["cat", "dog", "cat", "dog"],
        groups=["west", "west", "north", "north"],
    )

    assert list(result["slices"]) == ["north", "west"]


def test_mismatched_lengths_raise_error():
    with pytest.raises(ValueError, match="equal lengths"):
        classification_slice_metrics(
            actual=["cat", "dog"],
            predicted=["cat"],
            groups=["north", "south"],
        )


def test_blank_group_raises_error():
    with pytest.raises(ValueError, match="non-empty strings"):
        classification_slice_metrics(
            actual=["cat", "dog"],
            predicted=["cat", "dog"],
            groups=["north", " "],
        )


@pytest.mark.parametrize("value", [True, 1.5])
def test_invalid_minimum_group_size_type_raises_type_error(value):
    with pytest.raises(TypeError):
        classification_slice_metrics(
            actual=["cat"],
            predicted=["cat"],
            groups=["north"],
            min_group_size=value,
        )


@pytest.mark.parametrize("value", [0, -1])
def test_invalid_minimum_group_size_value_raises_value_error(value):
    with pytest.raises(ValueError):
        classification_slice_metrics(
            actual=["cat"],
            predicted=["cat"],
            groups=["north"],
            min_group_size=value,
        )


def test_accuracy_gap_is_none_with_one_evaluated_group():
    result = classification_slice_metrics(
        actual=["cat", "dog", "cat"],
        predicted=["cat", "dog", "cat"],
        groups=["north", "north", "west"],
        min_group_size=2,
    )

    assert result["accuracy_gap"] is None

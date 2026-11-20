from dslab.drift_numeric import compare_numeric, parse_numeric, summarize_numeric


def test_parse_numeric_values_and_ignore_missing_values():
    assert parse_numeric(["1", "", "3"]) == [1.0, 3.0]


def test_non_numeric_column_returns_none():
    assert parse_numeric(["1", "two"]) is None


def test_numeric_summary_contains_expected_statistics():
    summary = summarize_numeric([2.0, 4.0, 6.0])
    assert summary["count"] == 3.0
    assert summary["mean"] == 4.0
    assert summary["min"] == 2.0
    assert summary["max"] == 6.0


def test_numeric_comparison_detects_mean_change():
    result = compare_numeric([10.0, 12.0], [20.0, 22.0])
    assert result["mean_relative_change"] > 0.5
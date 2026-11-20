from dslab.drift_metrics import absolute_rate_change, missing_rate


def test_missing_rate_ignores_whitespace_only_values():
    assert missing_rate(["A", "", "  ", "B"]) == 0.5


def test_absolute_rate_change_is_absolute():
    assert absolute_rate_change(0.25, 0.0) == 0.25
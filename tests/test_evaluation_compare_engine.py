import json

import pytest

from dslab.evaluation_compare_engine import compare_evaluations


def write_report(path, metrics):
    path.write_text(json.dumps({"metrics": metrics}), encoding="utf-8")


def sample_metrics(**updates):
    metrics = {
        "accuracy": 0.9,
        "macro_precision": 0.9,
        "macro_recall": 0.9,
        "macro_f1": 0.9,
        "weighted_f1": 0.9,
    }
    metrics.update(updates)
    return metrics


def test_detects_metric_drop_beyond_threshold(tmp_path):
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    write_report(baseline, sample_metrics())
    write_report(candidate, sample_metrics(accuracy=0.8))
    report = compare_evaluations(baseline, candidate)
    assert report["status"] == "regression_detected"
    assert "accuracy" in report["regression_metrics"]


def test_allows_drops_within_threshold(tmp_path):
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    write_report(baseline, sample_metrics())
    write_report(candidate, sample_metrics(accuracy=0.88))
    report = compare_evaluations(baseline, candidate)
    assert report["status"] == "no_significant_regression"


def test_detects_multiple_metrics_and_preserves_deltas(tmp_path):
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    write_report(baseline, sample_metrics())
    write_report(candidate, sample_metrics(macro_recall=0.7, macro_f1=0.75))
    report = compare_evaluations(baseline, candidate)
    assert set(report["regression_metrics"]) == {"macro_recall", "macro_f1"}
    assert report["metric_comparisons"]["macro_recall"]["delta"] == -0.2


def test_rejects_metric_values_outside_unit_interval(tmp_path):
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    write_report(baseline, sample_metrics())
    write_report(candidate, sample_metrics(accuracy=1.2))
    with pytest.raises(ValueError, match="between 0 and 1"):
        compare_evaluations(baseline, candidate)


def test_rejects_boolean_threshold(tmp_path):
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    config = tmp_path / "config.json"
    write_report(baseline, sample_metrics())
    write_report(candidate, sample_metrics())
    config.write_text(
        json.dumps({"metric_drop_thresholds": {"accuracy": True}}),
        encoding="utf-8",
    )
    with pytest.raises(TypeError, match="Threshold must be numeric"):
        compare_evaluations(baseline, candidate, config)

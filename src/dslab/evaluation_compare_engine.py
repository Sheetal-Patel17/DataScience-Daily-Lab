import json
import math
from pathlib import Path

DEFAULT_THRESHOLDS = {
    "accuracy": 0.03,
    "macro_precision": 0.05,
    "macro_recall": 0.05,
    "macro_f1": 0.05,
    "weighted_f1": 0.05,
}


def _read_json_object(path: str | Path, description: str) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {description}: {path}") from exc
    if not isinstance(value, dict):
        raise TypeError(f"{description} must be a JSON object: {path}")
    return value


def _validate_metrics(report: dict, description: str) -> dict[str, float]:
    metrics = report.get("metrics")
    if not isinstance(metrics, dict):
        raise TypeError(f"{description} has no valid 'metrics' object.")
    validated = {}
    for name in DEFAULT_THRESHOLDS:
        value = metrics.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{description} is missing numeric metric: {name}")
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"Metric {name} in {description} must be between 0 and 1.")
        validated[name] = float(value)
    return validated


def _read_thresholds(config_path: str | Path | None) -> dict[str, float]:
    if config_path is None:
        return DEFAULT_THRESHOLDS.copy()
    config = _read_json_object(config_path, "threshold configuration")
    thresholds = config.get("metric_drop_thresholds")
    if not isinstance(thresholds, dict):
        raise TypeError("Configuration needs a 'metric_drop_thresholds' object.")
    unknown = set(thresholds) - set(DEFAULT_THRESHOLDS)
    if unknown:
        raise ValueError(f"Unknown regression metric(s): {', '.join(sorted(unknown))}")
    result = DEFAULT_THRESHOLDS.copy()
    for name, value in thresholds.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Threshold must be numeric: {name}")
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"Threshold for {name} must be between 0 and 1.")
        result[name] = float(value)
    return result


def compare_evaluations(
    baseline_path: str | Path,
    candidate_path: str | Path,
    config_path: str | Path | None = None,
) -> dict:
    baseline_report = _read_json_object(baseline_path, "baseline evaluation report")
    candidate_report = _read_json_object(candidate_path, "candidate evaluation report")
    baseline_metrics = _validate_metrics(baseline_report, "Baseline report")
    candidate_metrics = _validate_metrics(candidate_report, "Candidate report")
    thresholds = _read_thresholds(config_path)

    comparisons = {}
    regressions = []
    for name, threshold in thresholds.items():
        baseline_value = baseline_metrics[name]
        candidate_value = candidate_metrics[name]
        delta = candidate_value - baseline_value
        regressed = baseline_value - candidate_value > threshold
        comparisons[name] = {
            "baseline": round(baseline_value, 6),
            "candidate": round(candidate_value, 6),
            "delta": round(delta, 6),
            "allowed_drop": threshold,
            "regression_detected": regressed,
        }
        if regressed:
            regressions.append(name)

    return {
        "report_version": 1,
        "status": "regression_detected" if regressions else "no_significant_regression",
        "baseline_path": str(Path(baseline_path).resolve()),
        "candidate_path": str(Path(candidate_path).resolve()),
        "metric_comparisons": comparisons,
        "regression_metrics": regressions,
        "thresholds_are_absolute_score_drops": True,
        "notes": [
            "Metric values are assumed to be between 0 and 1, where higher is better.",
            "A regression is flagged only when the drop strictly exceeds its threshold.",
            "A comparison report is a screening aid, not a substitute for model review.",
        ],
    }

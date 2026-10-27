from dslab.drift_categorical import compare_categorical
from dslab.drift_data import read_csv_dataset
from dslab.drift_metrics import absolute_rate_change, missing_rate
from dslab.drift_numeric import compare_numeric, parse_numeric

DEFAULT_THRESHOLDS = {
    "missing_rate_delta_threshold": 0.10,
    "numeric_relative_change_threshold": 0.20,
    "categorical_total_variation_threshold": 0.20,
}


def _thresholds(config: dict) -> dict[str, float]:
    result = {}
    for key, default in DEFAULT_THRESHOLDS.items():
        value = config.get(key, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Threshold must be numeric: {key}")
        if value < 0 or (
            key != "numeric_relative_change_threshold" and value > 1
        ):
            raise ValueError(f"Threshold is outside its allowed range: {key}")
        result[key] = float(value)
    return result


def compare_datasets(baseline_path: str, current_path: str, config: dict) -> dict:
    thresholds = _thresholds(config)
    baseline_columns, baseline_rows = read_csv_dataset(baseline_path)
    current_columns, current_rows = read_csv_dataset(current_path)
    common_columns = [column for column in baseline_columns if column in current_columns]
    if not common_columns:
        raise ValueError("The datasets have no columns in common.")

    column_results = []
    for column in common_columns:
        baseline_values = [row[column] for row in baseline_rows]
        current_values = [row[column] for row in current_rows]
        baseline_missing = missing_rate(baseline_values)
        current_missing = missing_rate(current_values)
        missing_delta = absolute_rate_change(baseline_missing, current_missing)
        baseline_numeric = parse_numeric(baseline_values)
        current_numeric = parse_numeric(current_values)

        if baseline_numeric is not None and current_numeric is not None:
            distribution = compare_numeric(baseline_numeric, current_numeric)
            distribution_drifted = (
                distribution["mean_relative_change"]
                > thresholds["numeric_relative_change_threshold"]
                or distribution["std_relative_change"]
                > thresholds["numeric_relative_change_threshold"]
            )
        else:
            distribution = compare_categorical(baseline_values, current_values)
            distribution_drifted = (
                distribution["total_variation_distance"]
                > thresholds["categorical_total_variation_threshold"]
            )

        signals = []
        if missing_delta > thresholds["missing_rate_delta_threshold"]:
            signals.append("missing_rate_change")
        if distribution_drifted:
            signals.append("distribution_change")
        column_results.append({
            "column": column,
            "baseline_missing_rate": baseline_missing,
            "current_missing_rate": current_missing,
            "missing_rate_delta": missing_delta,
            "distribution": distribution,
            "drift_detected": bool(signals),
            "signals": signals,
        })

    drifted_count = sum(item["drift_detected"] for item in column_results)
    return {
        "status": "drift_detected" if drifted_count else "no_significant_drift",
        "baseline_rows": len(baseline_rows),
        "current_rows": len(current_rows),
        "columns_compared": len(common_columns),
        "columns_with_drift": drifted_count,
        "added_columns": [
            column for column in current_columns if column not in baseline_columns
        ],
        "removed_columns": [
            column for column in baseline_columns if column not in current_columns
        ],
        "thresholds": thresholds,
        "columns": column_results,
        "limitations": [
            "This is a screening signal, not proof that a model has degraded.",
            "Numeric drift uses mean and standard-deviation relative changes.",
            "Categorical drift uses total variation distance over observed values.",
            "Columns added or removed are listed but not distribution-compared.",
        ],
    }
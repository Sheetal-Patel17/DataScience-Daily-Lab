from collections import defaultdict

from dslab.classification_metrics import classification_metrics


def classification_slice_metrics(
    actual: list[str],
    predicted: list[str],
    groups: list[str],
    *,
    min_group_size: int = 2,
) -> dict:
    """Evaluate classification performance independently for each group."""
    if not isinstance(min_group_size, int) or isinstance(min_group_size, bool):
        raise TypeError("Minimum group size must be an integer.")
    if min_group_size < 1:
        raise ValueError("Minimum group size must be at least 1.")

    if not actual or not predicted or not groups:
        raise ValueError("Actual, predicted, and groups must not be empty.")

    if not (len(actual) == len(predicted) == len(groups)):
        raise ValueError("Actual, predicted, and groups must have equal lengths.")

    for name, values in (
        ("Actual labels", actual),
        ("Predicted labels", predicted),
        ("Group values", groups),
    ):
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"{name} must contain non-empty strings.")

    grouped = defaultdict(lambda: ([], []))

    for actual_label, predicted_label, group in zip(
        actual, predicted, groups, strict=True
    ):
        group = group.strip()
        grouped[group][0].append(actual_label.strip())
        grouped[group][1].append(predicted_label.strip())

    slices = {}
    warnings = []
    accuracies = []

    for group in sorted(grouped):
        group_actual, group_predicted = grouped[group]
        row_count = len(group_actual)

        if row_count < min_group_size:
            slices[group] = {
                "row_count": row_count,
                "status": "insufficient_data",
                "metrics": None,
                "per_class": None,
            }
            warnings.append(
                f"Group '{group}' has {row_count} rows; "
                f"minimum required is {min_group_size}."
            )
            continue

        result = classification_metrics(group_actual, group_predicted)

        slices[group] = {
            "row_count": row_count,
            "status": "evaluated",
            "metrics": result["metrics"],
            "per_class": result["per_class"],
        }

        accuracies.append(result["metrics"]["accuracy"])

    accuracy_gap = None

    if len(accuracies) >= 2:
        accuracy_gap = round(max(accuracies) - min(accuracies), 6)

        if accuracy_gap >= 0.15:
            warnings.append(
                "The difference between the highest and lowest group "
                "accuracy is at least 0.15."
            )

    return {
        "row_count": len(actual),
        "slice_count": len(slices),
        "evaluated_slice_count": len(accuracies),
        "accuracy_gap": accuracy_gap,
        "slices": slices,
        "warnings": warnings,
        "notes": [
            "Slice metrics describe observed predictions in each group.",
            "Small groups may have unstable metrics.",
            "Differences between groups are descriptive, not causal.",
            "This audit alone does not establish fairness or model bias.",
        ],
    }

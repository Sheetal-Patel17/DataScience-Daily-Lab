def _divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def classification_metrics(actual: list[str], predicted: list[str]) -> dict:
    """Calculate standard single-label classification metrics without dependencies."""
    if not actual or not predicted:
        raise ValueError("Actual and predicted labels must not be empty.")
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted label lists must have equal lengths.")
    if any(not label.strip() for label in actual + predicted):
        raise ValueError("Labels must be non-empty strings.")

    labels = sorted(set(actual) | set(predicted))
    per_class = {}
    confusion_matrix = {
        actual_label: {predicted_label: 0 for predicted_label in labels}
        for actual_label in labels
    }
    correct = 0
    for actual_label, predicted_label in zip(actual, predicted, strict=True):
        confusion_matrix[actual_label][predicted_label] += 1
        correct += actual_label == predicted_label

    for label in labels:
        true_positive = confusion_matrix[label][label]
        support = sum(actual_label == label for actual_label in actual)
        predicted_count = sum(predicted_label == label for predicted_label in predicted)
        false_positive = predicted_count - true_positive
        false_negative = support - true_positive
        precision = _divide(true_positive, true_positive + false_positive)
        recall = _divide(true_positive, true_positive + false_negative)
        f1 = _divide(2 * precision * recall, precision + recall)
        per_class[label] = {
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
            "support": support,
        }

    label_count = len(labels)
    total_rows = len(actual)
    macro_precision = (
        sum(item["precision"] for item in per_class.values()) / label_count
    )
    macro_recall = sum(item["recall"] for item in per_class.values()) / label_count
    macro_f1 = sum(item["f1"] for item in per_class.values()) / label_count

    def weighted(metric_name: str) -> float:
        return sum(
            item[metric_name] * item["support"] for item in per_class.values()
        ) / total_rows

    metrics = {
        "accuracy": correct / total_rows,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_precision": weighted("precision"),
        "weighted_recall": weighted("recall"),
        "weighted_f1": weighted("f1"),
    }
    return {
        "row_count": total_rows,
        "labels": labels,
        "metrics": {name: round(value, 6) for name, value in metrics.items()},
        "per_class": per_class,
        "confusion_matrix": confusion_matrix,
        "notes": [
            "Precision, recall, and F1 are calculated one-vs-rest for each label.",
            "Scores with a zero denominator are set to 0.0.",
            "This report describes predictions; it does not prove model "
            "generalization.",
        ],
    }

from collections import Counter


def category_proportions(values: list[str]) -> dict[str, float]:
    nonempty = [value.strip() for value in values if value.strip()]
    if not nonempty:
        return {}
    counts = Counter(nonempty)
    total = len(nonempty)
    return {category: count / total for category, count in counts.items()}


def total_variation_distance(baseline: list[str], current: list[str]) -> float:
    baseline_props = category_proportions(baseline)
    current_props = category_proportions(current)
    categories = set(baseline_props) | set(current_props)
    return 0.5 * sum(
        abs(baseline_props.get(category, 0.0) - current_props.get(category, 0.0))
        for category in categories
    )


def compare_categorical(baseline: list[str], current: list[str]) -> dict:
    return {
        "kind": "categorical",
        "baseline_proportions": category_proportions(baseline),
        "current_proportions": category_proportions(current),
        "total_variation_distance": total_variation_distance(baseline, current),
    }
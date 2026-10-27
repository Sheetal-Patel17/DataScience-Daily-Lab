def missing_rate(values: list[str]) -> float:
    if not values:
        return 0.0
    missing = sum(not value.strip() for value in values)
    return missing / len(values)


def absolute_rate_change(baseline_rate: float, current_rate: float) -> float:
    return abs(current_rate - baseline_rate)
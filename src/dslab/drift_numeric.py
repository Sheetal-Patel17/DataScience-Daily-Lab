from statistics import fmean, pstdev


def parse_numeric(values: list[str]) -> list[float] | None:
    nonempty = [value.strip() for value in values if value.strip()]
    if not nonempty:
        return None
    try:
        return [float(value) for value in nonempty]
    except ValueError:
        return None


def summarize_numeric(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("Cannot summarize an empty numeric column.")
    return {
        "count": float(len(values)),
        "mean": fmean(values),
        "std_dev": pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def relative_change(baseline: float, current: float) -> float:
    return abs(current - baseline) / max(abs(baseline), 1.0)


def compare_numeric(
    baseline_values: list[float], current_values: list[float]
) -> dict:
    baseline = summarize_numeric(baseline_values)
    current = summarize_numeric(current_values)
    return {
        "kind": "numeric",
        "baseline": baseline,
        "current": current,
        "mean_relative_change": relative_change(baseline["mean"], current["mean"]),
        "std_relative_change": relative_change(
            baseline["std_dev"], current["std_dev"]
        ),
    }
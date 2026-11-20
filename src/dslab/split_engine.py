import random
from collections import defaultdict
from math import isclose, isfinite

SPLIT_NAMES = ("train", "validation", "test")
DEFAULT_RATIOS = {"train": 0.7, "validation": 0.15, "test": 0.15}


def validate_ratios(ratios: dict) -> dict[str, float]:
    normalized = {}
    for name in SPLIT_NAMES:
        value = ratios.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"Split ratio must be numeric: {name}")
        if not isfinite(value) or value <= 0 or value >= 1:
            raise ValueError(f"Split ratio must be between 0 and 1: {name}")
        normalized[name] = float(value)
    if not isclose(sum(normalized.values()), 1.0, rel_tol=0.0, abs_tol=1e-8):
        raise ValueError("Train, validation, and test ratios must sum to 1.0.")
    return normalized


def allocate_counts(size: int, ratios: dict[str, float], ensure_each: bool = False) -> list[int]:
    raw = [size * ratios[name] for name in SPLIT_NAMES]
    counts = [int(value) for value in raw]
    remaining = size - sum(counts)
    priority = sorted(range(3), key=lambda index: raw[index] - counts[index], reverse=True)
    for index in priority[:remaining]:
        counts[index] += 1

    if ensure_each:
        for index, count in enumerate(counts):
            if count == 0:
                donors = [candidate for candidate, value in enumerate(counts) if value > 1]
                if not donors:
                    raise ValueError("At least three rows are required for three non-empty splits.")
                donor = max(donors, key=lambda candidate: counts[candidate])
                counts[donor] -= 1
                counts[index] += 1
    return counts


def _slice_by_counts(rows: list[dict[str, str]], counts: list[int]) -> dict[str, list[dict[str, str]]]:
    result = {}
    start = 0
    for name, count in zip(SPLIT_NAMES, counts, strict=True):
        result[name] = rows[start : start + count]
        start += count
    return result


def split_dataset(
    rows: list[dict[str, str]],
    columns: list[str],
    ratios: dict,
    seed: int = 42,
    stratify_by: str | None = None,
    group_column: str | None = None,
) -> dict[str, list[dict[str, str]]]:
    normalized_ratios = validate_ratios(ratios)
    if len(rows) < 3:
        raise ValueError("At least three data rows are required for train/validation/test splits.")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("Seed must be an integer.")
    if stratify_by and group_column:
        raise ValueError("Choose either --stratify-by or --group-column, not both.")
    for column in (stratify_by, group_column):
        if column and column not in columns:
            raise ValueError(f"Column not found in input CSV: {column}")

    rng = random.Random(seed)
    if stratify_by:
        buckets = {name: [] for name in SPLIT_NAMES}
        strata = defaultdict(list)
        for row in rows:
            strata[row[stratify_by]].append(row)
        for label in sorted(strata):
            group = strata[label]
            if len(group) < 3:
                raise ValueError(
                    f"Each stratum in '{stratify_by}' needs at least 3 rows; "
                    f"value {label!r} has {len(group)}."
                )
            rng.shuffle(group)
            counts = allocate_counts(len(group), normalized_ratios, ensure_each=True)
            parts = _slice_by_counts(group, counts)
            for name in SPLIT_NAMES:
                buckets[name].extend(parts[name])
        for name in SPLIT_NAMES:
            rng.shuffle(buckets[name])
        return buckets

    if group_column:
        groups = defaultdict(list)
        for row in rows:
            value = row[group_column]
            if not value:
                raise ValueError(f"Group column '{group_column}' contains a blank value.")
            groups[value].append(row)
        if len(groups) < 3:
            raise ValueError("Group-aware splitting requires at least three distinct groups.")
        shuffled_groups = list(groups.items())
        rng.shuffle(shuffled_groups)
        shuffled_groups.sort(key=lambda item: len(item[1]), reverse=True)
        targets = allocate_counts(len(rows), normalized_ratios, ensure_each=True)
        current_counts = [0, 0, 0]
        buckets = {name: [] for name in SPLIT_NAMES}

        for group_index, (_, group_rows) in enumerate(shuffled_groups):
            empty = [index for index, count in enumerate(current_counts) if count == 0]
            groups_left = len(shuffled_groups) - group_index
            candidates = empty if len(empty) >= groups_left else list(range(3))
            chosen = max(
                candidates,
                key=lambda index: (targets[index] - current_counts[index]) / max(targets[index], 1),
            )
            buckets[SPLIT_NAMES[chosen]].extend(group_rows)
            current_counts[chosen] += len(group_rows)
        for name in SPLIT_NAMES:
            rng.shuffle(buckets[name])
        return buckets

    shuffled = list(rows)
    rng.shuffle(shuffled)
    return _slice_by_counts(shuffled, allocate_counts(len(shuffled), normalized_ratios, ensure_each=True))
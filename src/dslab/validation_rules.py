"""Load and validate JSON rule configuration."""

import json
from pathlib import Path
from typing import Any

RULE_KEYS = {
    "required",
    "types",
    "ranges",
    "allowed_values",
    "string_lengths",
    "unique",
}

SUPPORTED_TYPES = {"string", "integer", "number", "boolean"}


def load_rules(path: str | Path) -> dict[str, Any]:
    """Load a rules JSON file and validate its basic structure."""
    with Path(path).open(encoding="utf-8-sig") as file:
        rules = json.load(file)

    if not isinstance(rules, dict):
        raise ValueError("Rules configuration must be a JSON object.")

    unknown = set(rules) - RULE_KEYS
    if unknown:
        raise ValueError(f"Unknown rule sections: {sorted(unknown)}")

    for key in ("required", "unique"):
        if key in rules and (
            not isinstance(rules[key], list)
            or not all(isinstance(item, str) for item in rules[key])
        ):
            raise ValueError(f"'{key}' must be a list of field names.")

    for section in ("types", "ranges", "allowed_values", "string_lengths"):
        if section in rules and not isinstance(rules[section], dict):
            raise ValueError(f"'{section}' must be a JSON object.")

    for field, kind in rules.get("types", {}).items():
        if kind not in SUPPORTED_TYPES:
            raise ValueError(
                f"Unsupported type '{kind}' for field '{field}'."
            )

    for section in ("ranges", "string_lengths"):
        for field, limits in rules.get(section, {}).items():
            if not isinstance(limits, dict):
                raise ValueError(f"Limits for '{field}' must be an object.")
            if set(limits) - {"min", "max"}:
                raise ValueError(f"Unknown limit for '{field}'.")
            if not limits:
                raise ValueError(f"Limits for '{field}' cannot be empty.")
            if not all(
                isinstance(value, (int, float)) and not isinstance(value, bool)
                for value in limits.values()
            ):
                raise ValueError(f"Limits for '{field}' must be numeric.")
            if (
                "min" in limits
                and "max" in limits
                and limits["min"] > limits["max"]
            ):
                raise ValueError(f"Minimum exceeds maximum for '{field}'.")

    for field, values in rules.get("allowed_values", {}).items():
        if not isinstance(values, list):
            raise ValueError(f"Allowed values for '{field}' must be a list.")

    return rules

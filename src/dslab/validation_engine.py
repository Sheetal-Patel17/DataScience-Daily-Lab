"""Apply configurable validation rules to dictionaries representing CSV rows."""

from typing import Any

from dslab.validation_models import ValidationIssue, ValidationReport


def _number(value: str, kind: str) -> int | float | None:
    try:
        if kind == "integer":
            # Reject values such as "2.5" rather than silently truncating.
            if not value.strip() or str(int(value)) != value.strip():
                return None
            return int(value)
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_rows(
    rows: list[dict[str, Any]],
    rules: dict[str, Any],
    source: str = "<memory>",
) -> ValidationReport:
    """Validate rows and return a report containing every detected issue."""
    issues: list[ValidationIssue] = []
    seen: dict[str, dict[str, int]] = {
        field: {} for field in rules.get("unique", [])
    }

    def add_issue(
        row_number: int,
        field: str,
        rule: str,
        message: str,
        value: Any,
    ) -> None:
        issues.append(
            ValidationIssue(
                row_number=row_number,
                field=field,
                rule=rule,
                message=message,
                value=value,
            )
        )

    for row_number, row in enumerate(rows, start=1):
        values = {
            key: "" if value is None else str(value).strip()
            for key, value in row.items()
        }

        for field in rules.get("required", []):
            if not values.get(field, ""):
                add_issue(
                    row_number, field, "required",
                    "Required value is missing.", values.get(field, ""),
                )

        parsed_numbers: dict[str, int | float] = {}
        for field, kind in rules.get("types", {}).items():
            value = values.get(field, "")
            if not value:
                continue

            if kind == "string":
                continue
            if kind == "boolean":
                if value.lower() not in {"true", "false"}:
                    add_issue(
                        row_number, field, "type",
                        "Expected true or false.", value,
                    )
                continue

            number = _number(value, kind)
            if number is None:
                add_issue(
                    row_number, field, "type",
                    f"Expected {kind}.", value,
                )
            else:
                parsed_numbers[field] = number

        for field, limits in rules.get("ranges", {}).items():
            value = values.get(field, "")
            if not value:
                continue
            number = parsed_numbers.get(field)
            if number is None:
                number = _number(value, "number")
            if number is None:
                continue
            if "min" in limits and number < limits["min"]:
                add_issue(
                    row_number, field, "range",
                    f"Value must be at least {limits['min']}.", value,
                )
            if "max" in limits and number > limits["max"]:
                add_issue(
                    row_number, field, "range",
                    f"Value must be at most {limits['max']}.", value,
                )

        for field, allowed in rules.get("allowed_values", {}).items():
            value = values.get(field, "")
            if value and value not in allowed:
                add_issue(
                    row_number, field, "allowed_values",
                    f"Value must be one of: {allowed}.", value,
                )

        for field, limits in rules.get("string_lengths", {}).items():
            value = values.get(field, "")
            if not value:
                continue
            if "min" in limits and len(value) < limits["min"]:
                add_issue(
                    row_number, field, "string_length",
                    f"Text must contain at least {limits['min']} characters.",
                    value,
                )
            if "max" in limits and len(value) > limits["max"]:
                add_issue(
                    row_number, field, "string_length",
                    f"Text must contain at most {limits['max']} characters.",
                    value,
                )

        for field, field_seen in seen.items():
            value = values.get(field, "")
            if not value:
                continue
            if value in field_seen:
                add_issue(
                    row_number, field, "unique",
                    f"Duplicate value; first seen in data row "
                    f"{field_seen[value]}.",
                    value,
                )
            else:
                field_seen[value] = row_number

    return ValidationReport(
        source=source,
        total_rows=len(rows),
        issues=issues,
    )

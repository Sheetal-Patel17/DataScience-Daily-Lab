def infer_value_type(value: str) -> str:
    value = value.strip()
    if not value:
        return "unknown"
    if value.lower() in {"true", "false"}:
        return "boolean"
    try:
        int(value)
        return "integer"
    except ValueError:
        pass
    try:
        float(value)
        return "number"
    except ValueError:
        return "string"


def infer_column_type(values: list[str]) -> str:
    types = {
        inferred
        for value in values
        if (inferred := infer_value_type(value)) != "unknown"
    }
    if not types:
        return "unknown"
    if len(types) == 1:
        return types.pop()
    if types <= {"integer", "number"}:
        return "number"
    return "mixed"

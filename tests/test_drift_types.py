from dslab.drift_types import infer_column_type, infer_value_type


def test_infer_basic_value_types():
    assert infer_value_type("42") == "integer"
    assert infer_value_type("4.2") == "number"
    assert infer_value_type("false") == "boolean"
    assert infer_value_type("hello") == "string"
    assert infer_value_type("") == "unknown"


def test_integer_and_decimal_values_are_numeric():
    assert infer_column_type(["1", "2.5", "3"]) == "number"


def test_inconsistent_values_are_mixed():
    assert infer_column_type(["12", "unknown text"]) == "mixed"


def test_blank_values_do_not_change_inferred_type():
    assert infer_column_type(["5", "", "7"]) == "integer"
